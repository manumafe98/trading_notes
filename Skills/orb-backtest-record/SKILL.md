---
name: orb-backtest-record
description: >
  Creates a new row in one of the three "Backtesting MNQ ORB" strategy datasources
  (Candle, FVG, or Combined). Receives all column values as parameters plus an
  orb_type string that is internally mapped to the correct datasource UUID.
  No schema alteration needed — all select/multi_select options already exist.
---

# ORB Backtest Record

Adds a row to one of the three **Backtesting MNQ ORB** strategy datasources — Candle, FVG, or Combined — using all column data provided as parameters.

## Orb Type → Datasource Mapping

The `orb_type` parameter is internally mapped to the correct datasource UUID:

| `orb_type` | Strategy | Datasource UUID |
|------------|----------|-----------------|
| `"Candle"` | Candle | `35e5f93d-99be-80f3-a705-000bf7e26656` |
| `"FVG"` | FVG | `35e5f93d-99be-80de-815f-000b2401174f` |
| `"Combined"` | Combined | `35e5f93d-99be-80fa-a16c-000bd0420563` |

## Parameters

| Parameter | Type | Required | Description | Valid Values |
|-----------|------|----------|-------------|--------------|
| `orb_type` | string | yes | Strategy variant, internally mapped to the correct datasource | `"Candle"`, `"FVG"`, `"Combined"` |
| `name` | string | yes | Page title | e.g. `"ORB Candle 06/04/2026"` |
| `date` | string | yes | Trade date in `dd/mm/yyyy` | e.g. `"06/04/2026"` |
| `day` | string | yes | Day of week | `"Monday"`, `"Tuesday"`, `"Wednesday"`, `"Thursday"`, `"Friday"` |
| `month` | string | yes | Full month name | `"January"`–`"December"` |
| `entry_time` | string | yes | Entry time | e.g. `"09:35"` |
| `duration_min` | number | yes | Trade duration in minutes | e.g. `15.5` |
| `direction` | string | yes | Trade direction | `"Long"`, `"Short"` |
| `liquidity_points` | array | yes | Liquidity levels hit | Array of strings from the 40 valid options (see below) |
| `orb_range_pts` | number | yes | ORB range in points | e.g. `42.5` |
| `pnl` | number | yes | Profit/Loss in points | e.g. `120.75`, `-45.0` |
| `result` | string | yes | Trade result | `"Win"`, `"Loss"` |
| `sl_distance_pts` | number | yes | Stop-loss distance in points | e.g. `8.25` |
| `link` | string | yes | TradingView screenshot URL | e.g. `"https://www.tradingview.com/x/..."` |

## Liquidity Points — valid options

```
PDH, PDL, PWH, PWL, PMH, PML, LDL, LDH, ASL, ASH,
SUN LDL, SUN LDH, SUN ASL, SUN ASH,
MON LDL, MON LDH, MON ASL, MON ASH,
TUE LDL, TUE LDH, TUE ASL, TUE ASH,
WED LDL, WED LDH, WED ASL, WED ASH,
THU LDL, THU LDH, THU ASL, THU ASH,
FRI LDL, FRI LDH, FRI ASL, FRI ASH,
SAT LDL, SAT LDH, SAT ASL, SAT ASH
```

## Instructions

### Step 1 — Map orb_type to datasource ID

Map the `orb_type` string to its datasource UUID using the table above:

| `orb_type` | → `data_source_id` |
|------------|---------------------|
| `"Candle"` | `35e5f93d-99be-80f3-a705-000bf7e26656` |
| `"FVG"` | `35e5f93d-99be-80de-815f-000b2401174f` |
| `"Combined"` | `35e5f93d-99be-80fa-a16c-000bd0420563` |

### Step 2 — Build the properties object

Map each parameter to its Notion column name and format according to type:

| Notion Column | Parameter | Type | Format |
|---------------|-----------|------|--------|
| `Name` | `name` | title | Plain string |
| `Date` | `date` | text | Plain string |
| `Day` | `day` | select | Plain string |
| `Month` | `month` | select | Plain string |
| `Entry_Time` | `entry_time` | text | Plain string |
| `Duration_min` | `duration_min` | number | Number (not string) |
| `Direction` | `direction` | select | Plain string |
| `Liquidity Points` | `liquidity_points` | multi_select | JSON-serialized array string |
| `ORB_Range_pts` | `orb_range_pts` | number | Number (not string) |
| `P&L` | `pnl` | number | Number (not string) |
| `Result` | `result` | select | Plain string |
| `SL_Distance_pts` | `sl_distance_pts` | number | Number (not string) |
| `Link` | `link` | url | Plain string |

**Critical format rules:**

- `select` columns → plain string: `"Long"`, `"Win"`, `"Wednesday"`
- `number` columns → JavaScript number (no quotes): `42.5`, `120.75`, `-45.0`
- `multi_select` columns → **JSON string** with escaped quotes: `"[\"PDH\",\"ASL\",\"PWH\"]"`
- `title`, `text`, `url` → plain string

### Step 3 — Create the page

```
notion_notion-create-pages
  parent: { data_source_id: "<mapped data_source_id from Step 1>" }
  pages:
    - properties:
        Name:                "ORB Candle 06/04/2026"
        Date:                "06/04/2026"
        Day:                 "Monday"
        Month:               "April"
        Entry_Time:          "09:35"
        Duration_min:        15.5
        Direction:           "Long"
        Liquidity Points:    "[\"PDH\", \"ASL\", \"PWH\"]"
        ORB_Range_pts:       42.5
        P&L:                 120.75
        Result:              "Win"
        SL_Distance_pts:     8.25
        Link:                "https://www.tradingview.com/x/test123"
```

### Step 4 — Report

Display a summary table to the user:

```
## Row created — ORB Candle — 06/04/2026

| Column | Value |
|--------|-------|
| Name | ORB Candle 06/04/2026 |
| Date | 06/04/2026 |
| Day | Monday |
| Month | April |
| Entry Time | 09:35 |
| Duration (min) | 15.5 |
| Direction | Long |
| Liquidity Points | PDH, ASL, PWH |
| ORB Range (pts) | 42.5 |
| P&L | +120.75 |
| Result | Win |
| SL Distance (pts) | 8.25 |
| Link | https://www.tradingview.com/x/test123 |
```

## Full example — actual tool call trace

For a Candle strategy trade on Monday April 6th 2026, Long, Win:

**Step 1:** `orb_type = "Candle"` → `data_source_id = "35e5f93d-99be-80f3-a705-000bf7e26656"`

```
notion_notion-create-pages
  parent: { data_source_id: "35e5f93d-99be-80f3-a705-000bf7e26656" }
  pages:
    - properties:
        Name:                "ORB Candle 06/04/2026"
        Date:                "06/04/2026"
        Day:                 "Monday"
        Month:               "April"
        Entry_Time:          "09:35"
        Duration_min:        15.5
        Direction:           "Long"
        Liquidity Points:    "[\"PDH\", \"ASL\", \"PWH\"]"
        ORB_Range_pts:       42.5
        P&L:                 120.75
        Result:              "Win"
        SL_Distance_pts:     8.25
        Link:                "https://www.tradingview.com/x/test123"
```

## Key identifiers

| Item | ID |
|------|-----|
| Database | `35e5f93d-99be-80c9-b869-c2834f418caa` |
| Candle datasource | `35e5f93d-99be-80f3-a705-000bf7e26656` |
| FVG datasource | `35e5f93d-99be-80de-815f-000b2401174f` |
| Combined datasource | `35e5f93d-99be-80fa-a16c-000bd0420563` |

## Guidelines

- No schema alteration needed — all select/multi_select options are already present across all three datasources
- The `orb_type` parameter is mapped internally to the correct datasource UUID (Step 1) — callers never need to know the UUIDs
- If `liquidity_points` is empty or `["N/A"]`, pass `"[\"N/A\"]"` as the JSON string value — `"N/A"` is a valid multi_select option in all three datasource schemas
- Number values (Duration_min, ORB_Range_pts, P&L, SL_Distance_pts) must be numbers, not strings — passing `"15.5"` instead of `15.5` will cause a validation error
- Multi_select values must use the exact option names listed in "Liquidity Points — valid options" above
- The `Name` (title) column convention is: `"ORB <Strategy> <date>"` (e.g., `"ORB Candle 06/04/2026"`)
