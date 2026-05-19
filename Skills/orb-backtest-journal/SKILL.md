---
name: orb-backtest-journal
description: >
  Creates a new row in the "Backtesting MNQ ORB Journal" Notion database.
  Receives trade execution parameters for the day, fetches forex factory
  events via the forex-factory-day-news skill for the given date, and
  populates Bank Holidays and High Impact News columns automatically with
  "{currency} - {event}" formatted labels. Unknown multi_select options are
  added to the datasource schema on the fly.
---

# ORB Backtest Journal

Adds a journal row to the **Backtesting MNQ ORB** database → **Backtesting MNQ ORB Journal** datasource, combining user-supplied trade flags with forex factory event data for the day.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | string | yes | Date in `dd/mm/yyyy` format (e.g., `"06/04/2026"`) |
| `orb_candle_has_trade` | string | yes | `"Yes"` or `"No"` |
| `orb_fvg_has_trade` | string | yes | `"Yes"` or `"No"` |
| `orb_combined_has_trade` | string | yes | `"Yes"` or `"No"` |

## Instructions

### Step 1 — Invoke forex-factory-day-news skill

Invoke the `forex-factory-day-news` skill with the given `date`. This skill fetches forex factory data and produces:

- `bank_holidays[]` — array of `{currency, event, time, impact}` objects
- `high_impact_events[]` — array of `{currency, event, time, impact}` objects

Example output for `06/04/2026`:

```json
{
  "date": "2026-04-06",
  "bank_holidays": [
    {"event": "Bank Holiday", "currency": "CHF", "time": "All Day", "impact": "holiday"},
    {"event": "French Bank Holiday", "currency": "EUR", "time": "All Day", "impact": "holiday"}
  ],
  "high_impact_events": [
    {"event": "ISM Services PMI", "currency": "USD", "time": "11:00am", "impact": "high"}
  ]
}
```

### Step 2 — Build multi_select label arrays

From the `Event` and `Currency` columns of both result tables (or directly from the JSON), construct labels as `"{currency} - {event}"`.

| Column | Source | Label format | Empty fallback |
|--------|--------|-------------|----------------|
| **Bank Holidays** | `bank_holidays[]` | `"{currency} - {event}"` | `["N/A"]` |
| **High Impact News** | `high_impact_events[]` | `"{currency} - {event}"` | `["N/A"]` |

**Example:**

- `bank_holiday_labels` = `["CHF - Bank Holiday", "EUR - French Bank Holiday"]`
- `high_impact_labels` = `["USD - ISM Services PMI"]`

### Step 3 — Update datasource schema (only if new options are needed)

The Notion MCP tool requires multi_select options to pre-exist in the schema. Fetch the current schema and only update if labels from Step 2 are missing.

First, fetch current options:

```
notion_notion-fetch
  id: "3645f93d-99be-80bf-b4d3-000b399edb29"
```

From the response, extract existing option names for `Bank Holidays` and `High Impact News`.

**Skip conditions** — skip the update for a column (or entirely) if:
- Both forex arrays were empty → both columns only need `"N/A"` which always exists
- All labels from Step 2 already appear in the column's existing options

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

### Step 4 — Create the journal page

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

### Step 5 — Report

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

For a weekend with no events:

**Step 1 output:**
```json
{"date": "2026-05-17", "bank_holidays": [], "high_impact_events": []}
```

**Step 2 labels:**
- `bank_holiday_labels` = `["N/A"]`
- `high_impact_labels` = `["N/A"]`

**Step 3:** Skipped (schema already has `N/A` for both).

**Step 4:**
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

- Step 3 is conditional: skip it when both arrays are empty OR all labels already exist in the schema. Otherwise missing options cause `validation_error` on page creation
- Always pass `N/A` as the first option when setting multi_select schemas to keep it present
- The date parameter is passed as-is (`dd/mm/yyyy`) to both the forex script and the Notion page
- If the forex factory script produces the same labels as a previous run, they already exist → schema update is a no-op (idempotent)
