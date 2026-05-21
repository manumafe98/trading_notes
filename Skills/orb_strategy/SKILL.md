---
name: orb-strategy
description: >
  Executes an ORB (Opening Range Breakout) trade simulation on the TradingView
  chart using bar replay mode. Supports three strategy variants — Candle, FVG,
  and Combined — each with different stop-loss and take-profit levels sourced
  from the "ORB + FVG [NY]" indicator. Use this skill when the user wants to
  run a complete ORB backtest: replay to a date/time, detect the breakout,
  extract entry/exit levels, place a position, identify key levels in the
  trade path, and determine whether the trade hits SL or TP.
---

# ORB Strategy

Runs a full ORB trade simulation on the TradingView chart via bar replay. The skill starts at a given date/time, waits for the ORB to break, extracts trade parameters based on the chosen strategy variant, places a position, reports confluent key levels, and steps forward until the trade resolves (SL or TP hit).

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | string | yes | Date in `dd/mm/yyyy` format (e.g., `"19/05/2026"`) |
| `time` | string | yes | Replay start time in `HH:MM` 24h format (e.g., `"10:35"`) |
| `day` | string | yes | Full day name: `"Monday"`, `"Tuesday"`, `"Wednesday"`, `"Thursday"`, `"Friday"` |
| `orb_type` | string | yes | Strategy variant: `"Candle"`, `"Fvg"`, or `"Combined"` |
| `session_end` | string | yes | Session cutoff time in `HH:MM` 24h format (e.g., `"12:00"`). If ORB breaks after this time, the trade is skipped. |

## SL / TP / Range Mapping

The `orb_type` parameter determines which table columns are used for stop-loss, take-profit, and the key-levels range. Entry is always `Candle Entry`.

| orb_type | Entry | SL | TP | Key Levels Range |
|----------|-------|----|----|------------------|
| `Candle` | Candle Entry | Candle Cover | Candle TP | Entry → Candle TP |
| `Fvg` | Candle Entry | FVG Cover | FVG TP | Entry → FVG TP |
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

Compare `Broke Time` against the `session_end` parameter:

- If `Broke Time > session_end` → **SKIP**. Report: `"ORB broke at {Broke Time} — outside session ({session_end}), no trade."` Stop here.
- Otherwise → proceed to Step 4.

### Step 4 — Extract trade parameters

Parse the ORB table to extract:

| Column | Always extracted? | Used for |
|--------|-------------------|----------|
| `ORB Operation` | Yes | Direction (LONG / SHORT) |
| `Candle Entry` | Yes | Entry price |
| `Broke Time` | Yes | Re-entry time calculation |

Then based on `orb_type`, extract the SL and TP columns:

| orb_type | SL column | TP column |
|----------|-----------|-----------|
| `Candle` | `Candle Cover` | `Candle TP` |
| `Fvg` | `FVG Cover` | `FVG TP` |
| `Combined` | `FVG Ext` | `FVG EXT TP` |

### Step 5 — Validate SL and TP values

Check the extracted SL and TP values:

- If **SL is null, empty, or `"-"`** → **SKIP**. Report: `"No valid {SL column name} — skipping {orb_type} strategy."` Stop here.
- If **TP is null, empty, or `"-"`** → **SKIP**. Report: `"No valid {TP column name} — skipping {orb_type} strategy."` Stop here.

> For the `Candle` strategy, Candle Cover and Candle TP should always have values. For `Fvg` and `Combined`, FVG levels can be missing when no valid FVG is present on the chart.

### Step 6 — Calculate re-entry time and replay there

Take `Broke Time` and add **1 hour and 1 minute**.

Example:
- Broke Time = `09:36` → re-entry time = `10:37`
- Broke Time = `09:37` → re-entry time = `10:38`

```
tradingview-mcp_replay_start
  date: <date>
  time: <re_entry_time>
```

### Step 7 — Draw the position

Use `draw_position` with the direction from `ORB Operation`:

- If `ORB Operation = LONG` → `direction: "long"`, entry below TP, SL below entry.
- If `ORB Operation = SHORT` → `direction: "short"`, entry above TP, SL above entry.

```
tradingview-mcp_draw_position
  direction: <"long" or "short">
  entry_price: <Candle Entry>
  stop_price: <SL from Step 4>
  target_price: <TP from Step 4>
```

### Step 8 — Run key-levels-in-range

Invoke the `key-levels-in-range` skill with:

| Parameter | Value |
|-----------|-------|
| `current_day_of_the_week` | The `day` parameter |
| `entry_price` | `Candle Entry` |
| `take_profit_price` | `TP` from Step 4 (varies per `orb_type`) |

Display the returned levels to the user.

### Step 9 — Step forward until SL or TP is touched

Loop:

1. Call `replay_step` to advance one bar.
2. Call `data_get_ohlcv` with `count: 1` (or a small count) to get the current bar.
3. Check if the bar's **high or low** touched the SL or TP:

**For LONG positions:**
- Bar **low ≤ SL** → **SL HIT**. Stop.
- Bar **high ≥ TP** → **TP HIT**. Stop.

**For SHORT positions:**
- Bar **high ≥ SL** → **SL HIT**. Stop.
- Bar **low ≤ TP** → **TP HIT**. Stop.

Repeat until one of these conditions is met (no time cutoff).

### Step 10 — Report result

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
| Re-entry Time | {re_entry_time} |
| Key Levels in Range | {levels} |
| Outcome | {SL HIT / TP HIT} |
| Result Time | {bar timestamp} |
```

## Full Example

**Inputs:**
- `date` = `"19/05/2026"`
- `time` = `"10:35"`
- `day` = `"Tuesday"`
- `orb_type` = `"Candle"`
- `session_end` = `"12:00"`

**Step 1:** `replay_start({ date: "2026-05-19", time: "10:35" })`

**Step 2:** `data_get_pine_tables({ study_filter: "ORB + FVG [NY]" })` → ORB Status already `BROKEN`.

**Step 3:** Broke Time = `09:36`. `09:36 ≤ 12:00` → proceed.

**Step 4:** `orb_type = "Candle"` → SL = Candle Cover (`28986.50`), TP = Candle TP (`29170.25`). Entry = `29047.75`. Operation = `LONG`.

**Step 5:** SL and TP both valid → proceed.

**Step 6:** `09:36 + 1:01 = 10:37` → `replay_start({ date: "2026-05-19", time: "10:37" })`

**Step 7:** `draw_position({ direction: "long", entry: 29047.75, stop: 28986.50, target: 29170.25 })`

**Step 8:** `key-levels-in-range("Tuesday", 29047.75, 29170.25)` → `["LDH"]`

**Step 9:** Step. At 10:40 bar, low = `28980.50` ≤ SL `28986.50` → **SL HIT**.

**Step 10:**

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
```

## Skip Examples

### Skip: Broke outside session

**Input:** `orb_type = "Candle"`, `session_end = "09:00"`

**Step 2:** ORB Status = `BROKEN`, Broke Time = `09:36`.

**Step 3:** `09:36 > 09:00` → **SKIP**.

→ Report: `"ORB broke at 09:36 — outside session (09:00), no trade."`

### Skip: Missing FVG values

**Input:** `orb_type = "Fvg"`

**Step 4:** FVG Cover = `"-"`

**Step 5:** SL is `"-"` → **SKIP**.

→ Report: `"No valid FVG Cover — skipping Fvg strategy."`

## Guidelines

- The chart must have the **"ORB + FVG [NY]"** indicator active. If the table returns no data, report the issue.
- For `key-levels-in-range`, the chart must also have **ICT Killzones** and **Key Levels** indicators active.
- Time comparisons in Step 3 are done as `HH:MM` string comparisons (lexicographic order works for zero-padded 24h times).
- The `+1h 1min` rule is fixed for all `orb_type` values.
- Entry is always `Candle Entry`, regardless of strategy type.
- When SL and TP are both null/`"-"`, report both missing columns in the skip message.
- All times are in the chart's configured timezone (interpreted by TradingView).
- After `replay_start` to re-entry time, the ORB indicator resets and the table shows `OPEN`. Always use the trade parameters captured during Step 2–4 — never re-fetch the table at re-entry.
