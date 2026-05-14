---
name: sync-skills
description: >
  Syncs SKILL.md files from the local repo (E:/repos/trading_notes/Skills/) to
  the global opencode config (C:/Users/Manumafe/.config/opencode/skills/).
  Auto-discovers new skills and creates/updates them automatically.
  Use this skill when the user asks about syncing skills, updating skills in
  the global config, adding newly created skills to opencode, or keeping
  local and global skill definitions in sync.
---

# Sync Skills

Synchronizes all skill definitions from the local repo to the global opencode config. This ensures the global opencode agent always has the latest skill definitions without manual copy-paste.

## Trigger

Load this skill when the user says anything like:
- "sync my skills"
- "update skills in global config"
- "add new skill to opencode"
- "skills are out of sync"
- "copy skills to global config"
- "why isn't my new skill showing up"
- "refresh skill definitions"

## How It Works

The script `scripts/sync-skills.py` auto-discovers all skill folders in the local repo's `Skills/` directory, reads each `SKILL.md` frontmatter to determine the canonical skill name, and copies them to the global opencode config.

## Usage

Run the sync script:

```bash
python scripts/sync-skills.py
```

### Optional: Dry Run

To preview what would change without actually writing files:

```bash
python scripts/sync-skills.py --dry-run
```

## What Gets Synced

- **Source of truth**: `E:/repos/trading_notes/Skills/<skill-folder>/SKILL.md`
- **Target**: `C:/Users/Manumafe/.config/opencode/skills/<skill-name>/SKILL.md`

The script:
1. Scans `Skills/` for folders containing `SKILL.md`
2. Extracts the `name:` field from YAML frontmatter as the canonical skill name
3. Creates new skill folders in global config if they don't exist
4. Updates existing skills if `SKILL.md` content has changed
5. Reports orphaned global skills (exist globally but not in the repo)

## Output Example

```
Found 3 local skill(s):
  - forex-factory-bank-holiday-fetch
  - forex-factory-high-impact-fetch
  - key-levels-in-range

  [CREATE] key-levels-in-range
  [UPDATE] forex-factory-high-impact-fetch
  [OK]     forex-factory-bank-holiday-fetch

Done. Created: 1, Updated: 1, Unchanged: 1
```

## Adding a New Skill

1. Create a folder in `E:/repos/trading_notes/Skills/<my-skill>/`
2. Add a `SKILL.md` with proper YAML frontmatter (must include `name:` and `description:`)
3. Run `python scripts/sync-skills.py`
4. The skill is now available in the global opencode config

## Guidelines

- Always run from the repo root: `E:/repos/trading_notes/`
- The script is idempotent — safe to run multiple times
- After syncing, the new/updated skills will be available in the next opencode session
- Do NOT manually copy SKILL.md files — always use the script to avoid drift
