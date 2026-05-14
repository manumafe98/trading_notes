---
name: sync-skills
description: >
  Syncs entire skill folders (SKILL.md + all companion files) from the local repo
  (E:/repos/trading_notes/Skills/) to the global opencode config
  (C:/Users/Manumafe/.config/opencode/skills/). Auto-discovers new skills,
  creates/updates them, and removes stale files. Use this skill when the user
  asks about syncing skills, updating skills in opencode, adding newly created
  skills, or keeping local and global skill definitions in sync.
---

# Sync Skills

Synchronizes entire skill folders from the local repo to the global opencode config. Each skill folder — including SKILL.md, scripts, assets, and any companion files — is compared file-by-file and synced. This ensures the global opencode agent always has the latest, complete skill definitions without manual copy-paste.

## Trigger

Load this skill when the user says anything like:
- "sync my skills"
- "update skills in opencode"
- "add new skill to opencode"
- "skills are out of sync"
- "copy skills to opencode config"
- "why isn't my new skill showing up"
- "refresh skill definitions"

## How It Works

The script `scripts/sync-skills.py` auto-discovers all skill folders in the local repo's `Skills/` directory, reads each `SKILL.md` frontmatter to determine the canonical skill name, and syncs the **entire folder contents** to the opencode global config.

## Usage

Run the sync script from the repo root:

```bash
python scripts/sync-skills.py
```

### Optional: Dry Run

To preview what would change without actually writing files:

```bash
python scripts/sync-skills.py --dry-run
```

## What Gets Synced

- **Source of truth**: `E:/repos/trading_notes/Skills/<skill-folder>/`
- **Target**: `C:/Users/Manumafe/.config/opencode/skills/<skill-name>/`

The script syncs **entire folders**, not just SKILL.md. This includes:
- `SKILL.md` — skill definition (required)
- `run.py` — companion scripts
- `requirements.txt` — Python dependencies
- Any other files in the skill folder

The script:
1. Scans `Skills/` for folders containing `SKILL.md`
2. Extracts the `name:` field from YAML frontmatter as the canonical skill name
3. Compares each file in the source folder against the target (byte-level diff)
4. Copies new or changed files to the target
5. Removes files from the target that no longer exist in the source
6. Reports orphaned global skills (exist globally but not in the repo)

## Output Example

The script prints a table with **Skill Name**, **Action**, and **Details** columns.

```
Found 4 local skill(s), 20 orphaned.

+------------------------------------+------------+----------------------------------------------------+
| Skill Name                         | Action     | Details                                            |
+------------------------------------+------------+----------------------------------------------------+
| key-levels-in-range                | CREATED    | New skill folder (1 file(s))                       |
| forex-factory-high-impact-fetch    | UPDATED    | ~SKILL.md, ~run.py                                 |
| forex-factory-bank-holiday-fetch   | UNCHANGED  | No changes                                         |
| sync-skills                        | UNCHANGED  | No changes                                         |
| branch-pr                          | ORPHANED   | Exists globally but not in repo                    |
| sdd-apply                          | ORPHANED   | Exists globally but not in repo                    |
+------------------------------------+------------+----------------------------------------------------+

Summary: 1 created, 1 updated, 2 unchanged, 2 orphaned
```

**Actions explained:**
- **CREATED** — Skill did not exist in global config; entire folder synced
- **UPDATED** — One or more files changed; overwritten with latest versions
- **UNCHANGED** — All files match; nothing done
- **ORPHANED** — Skill exists in global config but not in the local repo (stale/legacy)

## Adding a New Skill

1. Create a folder in `E:/repos/trading_notes/Skills/<my-skill>/`
2. Add a `SKILL.md` with proper YAML frontmatter (must include `name:` and `description:`)
3. Add any companion files (scripts, requirements, assets) to the same folder
4. Run `python scripts/sync-skills.py`
5. The skill and all its files are now available in the opencode global config

## Guidelines

- Always run from the repo root: `E:/repos/trading_notes/`
- The script is idempotent — safe to run multiple times
- Stale files in the global folder (not in the source) are automatically removed
- After syncing, the new/updated skills will be available in the next opencode session
- Do NOT manually copy skill files — always use the script to avoid drift