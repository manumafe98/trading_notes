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

# Config
SOURCE_ROOT = Path("E:/repos/trading_notes/Skills")
TARGET_ROOT = Path("C:/Users/Manumafe/.config/opencode/skills")


def extract_skill_name(skill_md_path: Path) -> str | None:
    """Read the YAML frontmatter from SKILL.md and extract the 'name' field."""
    try:
        content = skill_md_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ERROR: Cannot read {skill_md_path}: {e}")
        return None

    # Look for name: in the first 10 lines
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
            continue  # skip _shared

        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            print(f"  SKIP: {entry.name}/ — no SKILL.md found")
            continue

        skill_name = extract_skill_name(skill_md)
        if not skill_name:
            print(f"  WARN: {entry.name}/SKILL.md has no 'name:' in frontmatter, using folder name")
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


def sync_skills(dry_run: bool = False):
    """Main sync logic."""
    print(f"Source : {SOURCE_ROOT}")
    print(f"Target : {TARGET_ROOT}")
    print(f"Dry run: {dry_run}")
    print()

    local_skills = discover_local_skills()
    global_skills = discover_global_skills()

    if not local_skills:
        print("No local skills found to sync.")
        return

    print(f"Found {len(local_skills)} local skill(s):")
    for name in sorted(local_skills.keys()):
        print(f"  - {name}")
    print()

    synced = 0
    updated = 0
    unchanged = 0

    for skill_name, source_path in sorted(local_skills.items()):
        target_dir = TARGET_ROOT / skill_name
        target_path = target_dir / "SKILL.md"

        action = None

        if not target_path.exists():
            action = "CREATE"
        else:
            # Compare content
            source_content = source_path.read_text(encoding="utf-8")
            target_content = target_path.read_text(encoding="utf-8")
            if source_content != target_content:
                action = "UPDATE"
            else:
                action = "UNCHANGED"

        if action == "CREATE":
            print(f"  [CREATE] {skill_name}")
            if not dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
            synced += 1
        elif action == "UPDATE":
            print(f"  [UPDATE] {skill_name}")
            if not dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
            updated += 1
        else:
            print(f"  [OK]     {skill_name}")
            unchanged += 1

    # Check for orphaned global skills (exist globally but not locally)
    orphaned = global_skills - set(local_skills.keys())
    if orphaned:
        print(f"\n  Orphaned global skills (not in local repo): {len(orphaned)}")
        for name in sorted(orphaned):
            print(f"    - {name}")

    print(f"\nDone. Created: {synced}, Updated: {updated}, Unchanged: {unchanged}")
    if dry_run:
        print("(This was a dry run — no files were actually written.)")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    sync_skills(dry_run=dry_run)
