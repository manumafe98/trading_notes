#!/usr/bin/env python3
"""
sync-skills.py

Syncs entire skill folders from the local repo to the global opencode config.
Each skill folder (SKILL.md + all companion files) is compared file-by-file.

Usage:
    python scripts/sync-skills.py [--dry-run]

Source of truth: E:/repos/trading_notes/Skills/
Target:          C:/Users/Manumafe/.config/opencode/skills/
"""

import os
import re
import sys
import shutil
import filecmp
from pathlib import Path
from dataclasses import dataclass

SOURCE_ROOT = Path("E:/repos/trading_notes/Skills")
TARGET_ROOT = Path("C:/Users/Manumafe/.config/opencode/skills")


@dataclass
class SyncResult:
    name: str
    action: str
    detail: str = ""


def extract_skill_name(skill_md_path: Path) -> str | None:
    try:
        content = skill_md_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ERROR: Cannot read {skill_md_path}: {e}")
        return None

    for line in content.splitlines()[:10]:
        match = re.match(r'^name:\s*(.+?)\s*$', line)
        if match:
            return match.group(1).strip()
    return None


def get_relative_files(folder: Path) -> dict[str, Path]:
    files = {}
    for f in folder.rglob("*"):
        if f.is_file():
            files[str(f.relative_to(folder))] = f
    return files


def discover_local_skills() -> dict[str, Path]:
    skills = {}
    if not SOURCE_ROOT.exists():
        print(f"ERROR: Source directory does not exist: {SOURCE_ROOT}")
        sys.exit(1)

    for entry in SOURCE_ROOT.iterdir():
        if not entry.is_dir():
            continue
        if entry.name.startswith("_"):
            continue

        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue

        skill_name = extract_skill_name(skill_md)
        if not skill_name:
            skill_name = entry.name

        skills[skill_name] = entry

    return skills


def sync_shared_folder(dry_run: bool) -> SyncResult | None:
    shared_source = SOURCE_ROOT / "_shared"
    shared_target = TARGET_ROOT / "_shared"

    if not shared_source.exists():
        return None

    action, changes = sync_folder(shared_source, shared_target, dry_run)

    if action == "CREATED":
        detail = f"New shared folder ({len(get_relative_files(shared_source))} file(s))"
    elif action == "UPDATED":
        detail = ", ".join(changes[:5])
        if len(changes) > 5:
            detail += f" +{len(changes) - 5} more"
    else:
        detail = "No changes"

    return SyncResult(name="_shared", action=action, detail=detail)


def discover_global_skills() -> set[str]:
    skills = set()
    if not TARGET_ROOT.exists():
        return skills

    for entry in TARGET_ROOT.iterdir():
        if not entry.is_dir():
            continue
        if entry.name.startswith("_"):
            continue
        skills.add(entry.name)

    return skills


def sync_folder(source: Path, target: Path, dry_run: bool) -> tuple[str, list[str]]:
    source_files = get_relative_files(source)
    target_files = get_relative_files(target) if target.exists() else {}
    changes = []

    is_new = not target.exists()

    for rel_path, src_file in sorted(source_files.items()):
        tgt_file = target / rel_path

        if rel_path not in target_files:
            if not dry_run:
                tgt_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, tgt_file)
            changes.append(f"+{rel_path}")
        elif not filecmp.cmp(str(src_file), str(tgt_file), shallow=False):
            if not dry_run:
                tgt_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, tgt_file)
            changes.append(f"~{rel_path}")

    for rel_path in sorted(set(target_files) - set(source_files)):
        tgt_file = target / rel_path
        if not dry_run:
            tgt_file.unlink(missing_ok=True)
        changes.append(f"-{rel_path}")

    if is_new:
        action = "CREATED"
    elif changes:
        action = "UPDATED"
    else:
        action = "UNCHANGED"

    return action, changes


def clean_empty_dirs(folder: Path, dry_run: bool):
    if dry_run or not folder.exists():
        return
    for dirpath, dirnames, filenames in os.walk(folder, topdown=False):
        dp = Path(dirpath)
        if dp != folder and not any(dp.iterdir()):
            dp.rmdir()


def print_table(results: list[SyncResult]):
    if not results:
        print("  No skills to report.")
        return

    name_width = max(len(r.name) for r in results)
    action_width = max(len(r.action) for r in results)
    name_width = max(name_width, 11)
    action_width = max(action_width, 6)

    sep = f"+-{'-' * (name_width + 2)}-+-{'-' * (action_width + 2)}-+-{'-' * 50}-+"
    header = f"| {'Skill Name':<{name_width}} | {'Action':<{action_width}} | {'Details':<50} |"

    print(sep)
    print(header)
    print(sep)

    for r in results:
        print(f"| {r.name:<{name_width}} | {r.action:<{action_width}} | {r.detail:<50} |")

    print(sep)


def sync_skills(dry_run: bool = False):
    print(f"Source : {SOURCE_ROOT}")
    print(f"Target : {TARGET_ROOT}")
    print(f"Dry run: {dry_run}")
    print()

    local_skills = discover_local_skills()
    global_skills = discover_global_skills()

    if not local_skills:
        print("No local skills found to sync.")
        return

    results: list[SyncResult] = []

    shared_result = sync_shared_folder(dry_run)
    if shared_result:
        results.append(shared_result)

    for skill_name in sorted(local_skills.keys()):
        source_folder = local_skills[skill_name]
        target_folder = TARGET_ROOT / skill_name

        action, changes = sync_folder(source_folder, target_folder, dry_run)

        if action == "CREATED":
            src_count = len(get_relative_files(source_folder))
            detail = f"New skill folder ({src_count} file(s))"
        elif action == "UPDATED":
            detail = ", ".join(changes[:5])
            if len(changes) > 5:
                detail += f" +{len(changes) - 5} more"
        else:
            detail = "No changes"

        results.append(SyncResult(name=skill_name, action=action, detail=detail))

    for name in sorted(global_skills - set(local_skills.keys())):
        results.append(SyncResult(name=name, action="ORPHANED", detail="Exists globally but not in repo"))

    clean_empty_dirs(TARGET_ROOT, dry_run)

    action_order = {"CREATED": 0, "UPDATED": 1, "ORPHANED": 2, "UNCHANGED": 3, "ERROR": 4}
    results.sort(key=lambda r: (action_order.get(r.action, 5), r.name))

    print(f"Found {len(local_skills)} local skill(s), {len(global_skills - set(local_skills.keys()))} orphaned.\n")
    print_table(results)

    counts = {"CREATED": 0, "UPDATED": 0, "UNCHANGED": 0, "ORPHANED": 0, "ERROR": 0}
    for r in results:
        counts[r.action] = counts.get(r.action, 0) + 1

    print(f"\nSummary: {counts['CREATED']} created, {counts['UPDATED']} updated, "
          f"{counts['UNCHANGED']} unchanged, {counts['ORPHANED']} orphaned")

    if dry_run:
        print("\n(This was a dry run -- no files were actually written.)")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    sync_skills(dry_run=dry_run)