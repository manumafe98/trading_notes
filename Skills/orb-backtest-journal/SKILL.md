---
name: orb-backtest-journal
description: >
  Creates a new row in the "Backtesting MNQ ORB Journal" Notion database.
  Receives trade execution parameters for the day plus pre-fetched bank
  holidays and high-impact news labels, then populates Bank Holidays and
  High Impact News columns automatically with "{currency} - {event}"
  formatted labels. Unknown multi_select options are added to the
  datasource schema on the fly.
---

# ORB Backtest Journal

Adds a journal row to the **Backtesting MNQ ORB** database → **Backtesting MNQ ORB Journal** datasource, combining user-supplied trade flags with forex factory event data for the day.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | string | yes | Date in `dd/mm/yyyy` format (e.g., `"06/04/2026"`) |
| `bank_holiday_labels` | array | yes | Pre-formatted `string[]` labels in `"{currency} - {event}"` format (e.g., `["CHF - Bank Holiday"]`); caller handles formatting |
| `high_impact_labels` | array | yes | Pre-formatted `string[]` labels in `"{currency} - {event}"` format (e.g., `["USD - ISM Services PMI"]`); caller handles formatting |
| `orb_candle_has_trade` | string | yes | `"Yes"` or `"No"` |
| `orb_fvg_has_trade` | string | yes | `"Yes"` or `"No"` |
| `orb_combined_has_trade` | string | yes | `"Yes"` or `"No"` |

## Instructions

### Step 1 — Update datasource schema (only if new options are needed)

The Notion MCP tool requires multi_select options to pre-exist in the schema. Both `bank_holiday_labels` and `high_impact_labels` come pre-formatted from the caller. Fetch the current schema and only update if labels are missing.

First, fetch current options:

```
notion_notion-fetch
  id: "3645f93d-99be-80bf-b4d3-000b399edb29"
```

From the response, extract existing option names for `Bank Holidays` and `High Impact News`.

**Skip conditions** — skip the update for a column (or entirely) if:
- `bank_holiday_labels` is empty/`["N/A"]` AND `high_impact_labels` is empty/`["N/A"]` → both columns only need `"N/A"` which always exists
- All labels from both parameters already appear in the column's existing options

**Update if needed** — for each column with missing labels, merge existing + new (deduplicate):

```
notion_notion-update-data-source
  data_source_id: "3645f93d-99be-80bf-b4d3-000b399edb29"
  statements: >
    ALTER COLUMN "Bank Holidays" SET MULTI_SELECT('N/A','CHF - Bank Holiday','EUR - French Bank Holiday');
    ALTER COLUMN "High Impact News" SET MULTI_SELECT('N/A':red,'USD - ISM Services PMI')
```

Important rules:
- `ALTER COLUMN SET` **replaces** all options — always include existing + new
- Chain multiple statements with `;`
- Keep `N/A` with its red color for High Impact News: `'N/A':red`
- Colors are optional; omit for default
- This step becomes **idempotent**: after the first run for a given event set, subsequent runs skip it entirely

### Step 2 — Create the journal page

```
notion_notion-create-pages
  parent: { data_source_id: "3645f93d-99be-80bf-b4d3-000b399edb29" }
  pages:
    - properties:
        Date:                        "06/04/2026"
        Bank Holidays:               "[\"CHF - Bank Holiday\",\"EUR - French Bank Holiday\"]"
        High Impact News:            "[\"USD - ISM Services PMI\"]"
        Orb Candle has trade?:       "Yes"
        Orb FVG has trade?:          "No"
        Orb Combined has trade?:     "No"
```

**Critical format rules:**

| Property type | Format | Example |
|---------------|--------|---------|
| `title` (Date) | Plain string | `"06/04/2026"` |
| `select` (trade flags) | Plain string | `"Yes"` or `"No"` |
| `multi_select` (both news) | **JSON string** (double-escaped array) | `"[\"USD - ISM Services PMI\"]"` |

For multi_select with a single value: `"[\"N/A\"]"`
For multi_select with no values: `"[]"` (empty JSON array string)

### Step 3 — Report

Display a summary table to the user:

```
## Journal row created — 06/04/2026

| Column | Value |
|--------|-------|
| Date | 06/04/2026 |
| Bank Holidays | CHF - Bank Holiday, EUR - French Bank Holiday |
| High Impact News | USD - ISM Services PMI |
| Orb Candle has trade? | Yes |
| Orb FVG has trade? | No |
| Orb Combined has trade? | No |
```

## Full example — empty news day

For a weekend with no events, caller passes empty arrays:

**Parameters:**
- `bank_holiday_labels` = `["N/A"]`
- `high_impact_labels` = `["N/A"]`

**Step 1:** Skipped (schema already has `N/A` for both).

**Step 2:**
```
notion_notion-create-pages
  parent: { data_source_id: "3645f93d-99be-80bf-b4d3-000b399edb29" }
  pages:
    - properties:
        Date:                        "17/05/2026"
        Bank Holidays:               "[\"N/A\"]"
        High Impact News:            "[\"N/A\"]"
        Orb Candle has trade?:       "Yes"
        Orb FVG has trade?:          "No"
        Orb Combined has trade?:     "No"
```

## Key identifiers

| Item | ID |
|------|-----|
| Database | `35e5f93d-99be-80c9-b869-c2834f418caa` |
| Journal datasource | `3645f93d-99be-80bf-b4d3-000b399edb29` |

## Guidelines

- Step 1 is conditional: skip it when both arrays are empty/`["N/A"]` OR all labels already exist in the schema. Otherwise missing options cause `validation_error` on page creation
- Always pass `N/A` as the first option when setting multi_select schemas to keep it present
- Both `bank_holiday_labels` and `high_impact_labels` are passed pre-formatted by the caller (already `"{currency} - {event}"` format)
- If the same labels are produced as a previous run, they already exist → schema update is a no-op (idempotent)
