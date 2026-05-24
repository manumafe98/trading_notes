---
name: orb-strategy
description: >
  Executes an ORB (Opening Range Breakout) trade simulation on the TradingView
  chart using bar replay mode. Supports three strategy variants — Candle, FVG,
  and Combined — each with different stop-loss and take-profit levels sourced
  from the "ORB + FVG [NY]" indicator. At completion, persists the trade record
  to the corresponding Notion datasource via orb-backtest-record. Use this skill
  when the user wants to run a complete ORB backtest: replay to a date/time,
  detect the breakout, extract entry/exit levels, place a position, identify key
  levels in the trade path, determine whether the trade hits SL or TP, and
  record the result.
---

# ORB Strategy

Runs a full ORB trade simulation on the TradingView chart via bar replay. The skill starts at a given date/time, waits for the ORB to break, extracts trade parameters based on the chosen strategy variant, places a position, reports confluent key levels, steps forward until the trade resolves (SL or TP hit), and records the result to Notion via `orb-backtest-record`.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | string | yes | Date in `dd/mm/yyyy` format (e.g., `"19/05/2026"`) |
| `time` | string | yes | Replay start time in `HH:MM` 24h format (e.g., `"10:35"`) |
| `day` | string | yes | Full day name: `"Monday"`, `"Tuesday"`, `"Wednesday"`, `"Thursday"`, `"Friday"` |
| `month` | string | yes | Full month name: `"January"`–`"December"` (e.g., `"May"`) |
| `orb_type` | string | yes | Strategy variant: `"Candle"`, `"FVG"`, or `"Combined"` |
| `session_end` | string | yes | Session cutoff time in `HH:MM` 24h format (e.g., `"12:00"`). If ORB breaks after this time, the trade is skipped. |

## SL / TP / Range Mapping

The `orb_type` parameter determines which table columns are used for stop-loss, take-profit, and the key-levels range. Entry is always `Candle Entry`.

| orb_type | Entry | SL | TP | Key Levels Range |
|----------|-------|----|----|------------------|
| `Candle` | Candle Entry | Candle Cover | Candle TP | Entry → Candle TP |
| `FVG` | Candle Entry | FVG Cover | FVG TP | Entry → FVG TP |
| `Combined` | Candle Entry | FVG Ext | FVG EXT TP | Entry → FVG EXT TP |

## Instructions

### Step 1 — Start bar replay

```
tradingview-mcp_replay_start
  date: <date>
  time: <time>
```

This positions the chart at the requested date and time.

### Step 2 — Fetch ORB table and step until BROKEN

Call `data_get_pine_tables` with `study_filter: "ORB + FVG [NY]"`.

Parse the table rows. Look at the row labeled `ORB Status`:

- If `ORB Status` is **not** `BROKEN` → call `replay_step`, then call `data_get_pine_tables` again. Repeat until `ORB Status` becomes `BROKEN`.
- If `ORB Status` is already `BROKEN` → proceed to Step 3.

### Step 3 — Check session cutoff

From the table, extract the `Broke Time` value (format `HH:MM`).

Calculate the re-entry time: `Broke Time + 1h`. Compare the **re-entry time** against the `session_end` parameter:

- If `re-entry_time > session_end` → **SKIP**. Report: `"ORB broke at {Broke Time} (re-entry at {re-entry_time}) — outside session ({session_end}), no trade."` Stop here.
- Otherwise → proceed to Step 4.

### Step 4 — Extract trade parameters

Parse the ORB table to extract:

| Column | Always extracted? | Used for |
|--------|-------------------|----------|
| `ORB Operation` | Yes | Direction (LONG / SHORT) |
| `ORB High` | Yes | ORB range calculation |
| `ORB Low` | Yes | ORB range calculation |
| `Candle Entry` | Yes | Entry price |
| `Broke Time` | Yes | Re-entry time calculation |

Then based on `orb_type`, extract the SL and TP columns:

| orb_type | SL column | TP column |
|----------|-----------|-----------|
| `Candle` | `Candle Cover` | `Candle TP` |
| `FVG` | `FVG Cover` | `FVG TP` |
| `Combined` | `FVG Ext` | `FVG EXT TP` |

### Step 5 — Validate SL and TP values

Check the extracted SL and TP values:

- If **SL is null, empty, or `"-"`** → **SKIP**. Report: `"No valid {SL column name} — skipping {orb_type} strategy."` Stop here.
- If **TP is null, empty, or `"-"`** → **SKIP**. Report: `"No valid {TP column name} — skipping {orb_type} strategy."` Stop here.

> For the `Candle` strategy, Candle Cover and Candle TP should always have values. For `FVG` and `Combined`, FVG levels can be missing when no valid FVG is present on the chart.

### Step 6 — Calculate entry times and replay

Two entry times are derived from `Broke Time`:

| Time | Formula | Purpose |
|------|---------|---------|
| **Replay entry time** | Broke Time + 1h 1min | Bar replay positioning (where to place the chart) |
| **Entry time** (for recording) | Broke Time + 1h | Logical entry time (what gets recorded in Notion) |

Example:
- Broke Time = `09:36` → replay entry time = `10:37`, entry time = `10:36`
- Broke Time = `09:37` → replay entry time = `10:38`, entry time = `10:37`

Move the chart to the replay entry time:

```
tradingview-mcp_replay_start
  date: <date>
  time: <replay_entry_time>
```

### Step 7 — Draw the position and calculate SL distance

Use `draw_position` with the direction from `ORB Operation`:

- If `ORB Operation = LONG` → `direction: "long"`, entry below TP, SL below entry.
- If `ORB Operation = SHORT` → `direction: "short"`, entry above TP, SL above entry.

```
tradingview-mcp_draw_position
  direction: <"long" or "short">
  entry_price: <Candle Entry>
  stop_price: <SL from Step 4>
  target_price: <TP from Step 4>
  auto_zoom: true
  center_price: <ORB High if LONG, ORB Low if SHORT>
```

- For **LONG**, `center_price` = `ORB High` (the breakout level price crossed above).
- For **SHORT**, `center_price` = `ORB Low` (the breakout level price crossed below).

After drawing, calculate the stop-loss distance in points:

- **LONG**: `sl_distance_pts = Candle Entry - SL`
- **SHORT**: `sl_distance_pts = SL - Candle Entry`

Store this value for the recording step.

### Step 8 — Capture the TradingView screenshot link

Call `get_screenshot_link` to obtain a shareable TradingView chart URL:

```
tradingview-mcp_get_screenshot_link
```

Store the returned URL as `link` for use in the recording step.

### Step 9 — Run key-levels-in-range

Invoke the `key-levels-in-range` skill with:

| Parameter | Value |
|-----------|-------|
| `current_day_of_the_week` | The `day` parameter |
| `entry_price` | `Candle Entry` |
| `take_profit_price` | `TP` from Step 4 (varies per `orb_type`) |

Store the returned array as `liquidity_points`. Display the levels to the user. If the array is empty `[]`, use `"N/A"` as the value for `liquidity_points`.

### Step 10 — Step forward until SL or TP is touched

Loop:

1. Call `replay_step` to advance one bar.
2. Call `data_get_ohlcv` with `count: 1` (or a small count) to get the current bar.
3. Check if the bar's **high or low** touched the SL or TP:

**For LONG positions:**
- Bar **low ≤ SL** → **SL HIT**. Capture the bar time as `result_time`. Stop.
- Bar **high ≥ TP** → **TP HIT**. Capture the bar time as `result_time`. Stop.

**For SHORT positions:**
- Bar **high ≥ SL** → **SL HIT**. Capture the bar time as `result_time`. Stop.
- Bar **low ≤ TP** → **TP HIT**. Capture the bar time as `result_time`. Stop.

Repeat until one of these conditions is met (no time cutoff).

### Step 11 — Calculate derived values for recording

Compute all values needed by `orb-backtest-record`:

| Value | Formula / Source |
|-------|------------------|
| `name` | `"ORB {orb_type} {date}"` |
| `entry_time` | Broke Time + 1h (from Step 6) |
| `orb_range_pts` | ORB High - ORB Low (direct price difference) |
| `duration_min` | Minutes between `entry_time` and `result_time` |
| `direction` | `"Long"` if ORB Operation = `LONG`, `"Short"` if `SHORT` |
| `pnl` | `2` if TP hit, `-1` if SL hit |
| `result` | `"Win"` if TP hit, `"Loss"` if SL hit |
| `link` | The URL from `get_screenshot_link` (Step 8) |

> **duration_min example:** entry_time = `10:36`, result_time = `10:45` → duration_min = `9`

### Step 12 — Invoke orb-backtest-record

Invoke the `orb-backtest-record` skill with all collected and derived data:

```
orb-backtest-record(
  orb_type:          <orb_type>,
  name:              <derived name>,
  date:              <date>,
  day:               <day>,
  month:             <month>,
  entry_time:        <entry_time from Step 10>,
  duration_min:      <derived>,
  direction:         <derived>,
  liquidity_points:  <from key-levels-in-range>,
  orb_range_pts:     <ORB High - ORB Low>,
  pnl:               <2 or -1>,
  result:            <"Win" or "Loss">,
  sl_distance_pts:   <from Step 7>,
  link:              <from get_screenshot_link>
)
```

### Step 13 — Report result

State the outcome:

```
## ORB Strategy Result — {date}

| Field | Value |
|-------|-------|
| Strategy | {orb_type} |
| Direction | {ORB Operation} |
| Entry | {Candle Entry} |
| SL | {SL value} ({SL column name}) |
| TP | {TP value} ({TP column name}) |
| Broke Time | {Broke Time} |
| Re-entry Time | {replay_entry_time} |
| Key Levels in Range | {levels} |
| Outcome | {SL HIT / TP HIT} |
| Result Time | {result_time} |
| SL Distance (pts) | {sl_distance_pts} |
| ORB Range (pts) | {orb_range_pts} |
| Duration (min) | {duration_min} |
| P&L | {pnl} |
| Record | Created in {orb_type} datasource |
```

## Full Example

**Inputs:**
- `date` = `"19/05/2026"`
- `time` = `"10:35"`
- `day` = `"Tuesday"`
- `month` = `"May"`
- `orb_type` = `"Candle"`
- `session_end` = `"12:00"`

**Step 1:** `replay_start({ date: "2026-05-19", time: "10:35" })`

**Step 2:** `data_get_pine_tables({ study_filter: "ORB + FVG [NY]" })` → ORB Status already `BROKEN`.

**Step 3:** Broke Time = `09:36` → re-entry = `09:36 + 1h = 10:36`. `10:36 ≤ 12:00` → proceed.

**Step 4:** `orb_type = "Candle"` → SL = Candle Cover (`28986.50`), TP = Candle TP (`29170.25`). Entry = `29047.75`. Operation = `LONG`. ORB High = `29055.00`. ORB Low = `29010.25`.

**Step 5:** SL and TP both valid → proceed.

**Step 6:** `09:36 + 1h 1m = 10:37` (replay entry). `09:36 + 1h = 10:36` (entry time). → `replay_start({ date: "2026-05-19", time: "10:37" })`

**Step 7:** `draw_position({ direction: "long", entry: 29047.75, stop: 28986.50, target: 29170.25, auto_zoom: true, center_price: 29055.00 })` → `sl_distance_pts = 29047.75 - 28986.50 = 61.25`

**Step 8:** `get_screenshot_link()` → `"https://www.tradingview.com/x/abc123"`

**Step 9:** `key-levels-in-range("Tuesday", 29047.75, 29170.25)` → `["LDH"]` → stored as `liquidity_points`

**Step 10:** Step. At 10:40 bar, low = `28980.50` ≤ SL `28986.50` → **SL HIT**. result_time = `10:40`.

**Step 11:**
- `name` = `"ORB Candle 19/05/2026"`
- `entry_time` = `"10:36"`
- `orb_range_pts` = `29055.00 - 29010.25 = 44.75`
- `duration_min` = `10:40 - 10:36 = 4`
- `direction` = `"Long"`
- `pnl` = `-1`
- `result` = `"Loss"`
- `link` = from `get_screenshot_link`

**Step 12:** Invoke `orb-backtest-record` with all 14 parameters → row created in Candle datasource.

**Step 13:**

```
## ORB Strategy Result — 19/05/2026

| Field | Value |
|-------|-------|
| Strategy | Candle |
| Direction | LONG |
| Entry | 29047.75 |
| SL | 28986.50 (Candle Cover) |
| TP | 29170.25 (Candle TP) |
| Broke Time | 09:36 |
| Re-entry Time | 10:37 |
| Key Levels in Range | LDH |
| Outcome | SL HIT |
| Result Time | 10:40 |
| SL Distance (pts) | 61.25 |
| ORB Range (pts) | 44.75 |
| Duration (min) | 4 |
| P&L | -1 |
| Record | Created in Candle datasource |
```

## Skip Examples

### Skip: Broke outside session

**Input:** `orb_type = "Candle"`, `session_end = "09:00"`

**Step 2:** ORB Status = `BROKEN`, Broke Time = `09:36`.

**Step 3:** Re-entry = `09:36 + 1h = 10:36`. `10:36 > 09:00` → **SKIP**.

→ Report: `"ORB broke at 09:36 (re-entry at 10:36) — outside session (09:00), no trade."`

### Skip: Missing FVG values

**Input:** `orb_type = "FVG"`

**Step 4:** FVG Cover = `"-"`

**Step 5:** SL is `"-"` → **SKIP**.

→ Report: `"No valid FVG Cover — skipping FVG strategy."`

## Guidelines

- The chart must have the **"ORB + FVG [NY]"** indicator active. If the table returns no data, report the issue.
- For `key-levels-in-range`, the chart must also have **ICT Killzones** and **Key Levels** indicators active.
- Time comparisons in Step 3 are done as `HH:MM` string comparisons (lexicographic order works for zero-padded 24h times).
- The replay entry time adds **+1h 1min** to Broke Time — this is for bar replay positioning only. The logical entry time (recorded) adds **+1h** only.
- Entry is always `Candle Entry`, regardless of strategy type.
- When SL and TP are both null/`"-"`, report both missing columns in the skip message.
- All times are in the chart's configured timezone (interpreted by TradingView).
- After `replay_start` to replay entry time, the ORB indicator resets and the table shows `OPEN`. Always use the trade parameters captured during Step 2–4 — never re-fetch the table at re-entry.
- **Step 12** invokes `orb-backtest-record` to persist the trade to Notion. If the record skill is unavailable, display a warning but continue with the report.
- `sl_distance_pts`, `orb_range_pts`, and `duration_min` are all positive numbers.
