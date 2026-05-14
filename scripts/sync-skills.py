#!/usr/bin/env python3
"""
sync-skills.py

Syncs SKILL.md files from the local repo to the global opencode config.
Auto-discovers skills and creates/updates them in the global config.

Usage:
    python scripts/sync-skills.py [--dry-run]

Source of truth: E:/repos/trading_notes/Skills/
Target:          C:/Users/Manumafe/.config/opencode/skills/
"""

import os
import re
import sys
import shutil
from pathlib import Path
from dataclasses import dataclass

# Config
SOURCE_ROOT = Path("E:/repos/trading_notes/Skills")
TARGET_ROOT = Path("C:/Users/Manumafe/.config/opencode/skills")


@dataclass
class SkillResult:
    name: str
    action: str  # CREATED, UPDATED, UNCHANGED, ORPHANED, ERROR
    detail: str = ""


def extract_skill_name(skill_md_path: Path) -> str | None:
    """Read the YAML frontmatter from SKILL.md and extract the 'name' field."""
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


def discover_local_skills() -> dict[str, Path]:
    """Scan Skills/ folder and return {skill_name: local_skill_md_path}."""
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

        skills[skill_name] = skill_md

    return skills


def discover_global_skills() -> set[str]:
    """Return set of skill names currently in global config."""
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


def print_table(results: list[SkillResult]):
    """Print a simple two-column ASCII table."""
    if not results:
        print("  No skills to report.")
        return

    # Calculate column widths
    name_width = max(len(r.name) for r in results)
    action_width = max(len(r.action) for r in results)
    name_width = max(name_width, 11)  # min header width
    action_width = max(action_width, 6)  # min header width

    # Header
    sep = f"+-{'-' * (name_width + 2)}-+{'-' * (action_width + 2)}-+-{'-' * 50}-+"
    header = f"| {'Skill Name':<{name_width}} | {'Action':<{action_width}} | {'Details':<50} |"

    print(sep)
    print(header)
    print(sep)

    # Rows
    for r in results:
        print(f"| {r.name:<{name_width}} | {r.action:<{action_width}} | {r.detail:<50} |")

    print(sep)


def sync_skills(dry_run: bool = False):
    """Main sync logic with table report."""
    print(f"Source : {SOURCE_ROOT}")
    print(f"Target : {TARGET_ROOT}")
    print(f"Dry run: {dry_run}")
    print()

    local_skills = discover_local_skills()
    global_skills = discover_global_skills()

    if not local_skills:
        print("No local skills found to sync.")
        return

    results: list[SkillResult] = []

    # Process local skills
    for skill_name in sorted(local_skills.keys()):
        source_path = local_skills[skill_name]
        target_dir = TARGET_ROOT / skill_name
        target_path = target_dir / "SKILL.md"

        if not target_path.exists():
            if not dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
            results.append(SkillResult(name=skill_name, action="CREATED", detail="New skill added"))
        else:
            source_content = source_path.read_text(encoding="utf-8")
            target_content = target_path.read_text(encoding="utf-8")
            if source_content != target_content:
                if not dry_run:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, target_path)
                results.append(SkillResult(name=skill_name, action="UPDATED", detail="SKILL.md changed"))
            else:
                results.append(SkillResult(name=skill_name, action="UNCHANGED", detail="No changes"))

    # Check orphaned global skills
    orphaned = global_skills - set(local_skills.keys())
    for name in sorted(orphaned):
        results.append(SkillResult(name=name, action="ORPHANED", detail="Exists globally but not in repo"))

    # Sort results: CREATED, UPDATED, ORPHANED, UNCHANGED, ERROR
    action_order = {"CREATED": 0, "UPDATED": 1, "ORPHANED": 2, "UNCHANGED": 3, "ERROR": 4}
    results.sort(key=lambda r: (action_order.get(r.action, 5), r.name))

    # Print report
    print(f"Found {len(local_skills)} local skill(s), {len(orphaned)} orphaned.\n")
    print_table(results)

    # Summary
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
