---
name: orb-strategy-orchestrator
description: >
  Orchestrates multi-date, multi-strategy ORB backtests. Iterates over
  session-period objects (matching fetch-dates output), runs forex factory
  news lookup, executes Candle → FVG → Combined ORB strategies sequentially
  per date, and journals the daily result. First iteration — will later
  accept month/year and call fetch-dates internally.
  Trigger: When the user wants to run a batch of ORB backtests across
  multiple dates, or says "run orb orchestrator", "backtest all strategies
  for [month]", or provides session-period objects for batch processing.
---

# ORB Strategy Orchestrator

Receives an array of session-period objects (max 2, matching the `fetch-dates` output format) and runs all three ORB strategy variants — Candle, FVG, Combined — for every date in each object, plus forex factory news lookup and journal recording per date.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_periods` | array | yes | Array of 1–2 objects matching `fetch-dates` output format (see below) |

Each object in `session_periods`:

| Field | Type | Description |
|-------|------|-------------|
| `time` | string | NY session start in `HH:MM` 24h format (e.g., `"10:35"`) |
| `hour_diff` | number | Hours to add when converting NY (ET) to Argentina local time (`1` in EDT, `2` in EST) |
| `session_end` | string | NY session end in `HH:MM` 24h format (e.g., `"13:00"`) |
| `month` | string | Full month name (e.g., `"June"`, `"December"`) |
| `dates` | array | Array of `{ day, date }` objects for the weekdays in this period |

Each date object:

| Field | Type | Description |
|-------|------|-------------|
| `day` | string | Full weekday name (e.g., `"Monday"`) |
| `date` | string | Date in `dd/mm/yyyy` format (e.g., `"01/06/2026"`) |

### Input Example

```json
[
  {
    "time": "10:35",
    "hour_diff": 1,
    "session_end": "13:00",
    "month": "June",
    "dates": [
      {"day": "Monday",    "date": "01/06/2026"},
      {"day": "Tuesday",   "date": "02/06/2026"},
      {"day": "Wednesday", "date": "03/06/2026"}
    ]
  }
]
```

## Journal Model

A temporary state object, created fresh per date iteration and wiped after each journal record:

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `orb_candle_has_trade` | string | Did Candle strategy execute? | — |
| `orb_fvg_has_trade` | string | Did FVG strategy execute? | — |
| `orb_combined_has_trade` | string | Did Combined strategy execute? | — |
| `bank_holiday_labels` | string[] | Bank holiday labels in `"{currency} - {event}"` format | — |
| `high_impact_labels` | string[] | High-impact news labels in `"{currency} - {event}"` format | — |

All trade flags use `"Yes"` or `"No"`. Empty news arrays are stored as `["N/A"]`.

---

## Instructions

### Outer Loop — Iterate Over Session Periods

For each object `sp` in the `session_periods` array (max 2):

1. Extract `sp.time`, `sp.hour_diff`, `sp.session_end`, `sp.month`
2. Proceed to the **Inner Loop** over `sp.dates`

### Inner Loop — Iterate Over Dates

For each entry `d` in the current period's `dates` array:

1. Initialize the **Journal Model** with all trade flags unset
2. Run **Task 1** through **Task 5** sequentially
3. After Task 5, wipe the journal model and continue to the next date

---

### Task 1 — Forex Factory Day News

Invoke the `forex-factory-day-news` skill with the current date:

```
forex-factory-day-news:
  date: <d.date>
```

The skill returns JSON with `bank_holidays` and `high_impact_events` arrays.

**Format labels** from the response into `"{currency} - {event}"` format:

- For each bank holiday: `"{currency} - {event}"` → push to `bank_holiday_labels`
- For each high-impact event: `"{currency} - {event}"` → push to `high_impact_labels`

**After formatting:**

- If `bank_holiday_labels` is empty → set to `["N/A"]`
- If `high_impact_labels` is empty → set to `["N/A"]`

**If the forex-factory-day-news skill fails or returns an error:**
- Set both `bank_holiday_labels` and `high_impact_labels` to `["N/A"]`
- Log a warning: `"Forex Factory fetch failed for {d.date} — using N/A for news."`
- Continue to Task 2

---

### Task 2 — Candle Strategy

Invoke the `orb-strategy` skill with Candle as the strategy variant:

```
orb-strategy:
  date:         <d.date>
  time:         <sp.time>
  day:          <d.day>
  month:        <sp.month>
  orb_type:     "Candle"
  session_end:  <sp.session_end>
  hour_diff:    <sp.hour_diff>
```

**Determine outcome from the orb-strategy report:**

The Candle strategy may **SKIP** (no trade) for these reasons:
- ORB did not break
- ORB broke outside session cutoff
- Candle Cover or Candle TP is null / `"-"`

Watch the output for phrases like `"no trade"`, `"SKIP"`, `"outside session"`, `"No valid"`, or `"skipping"`.

**Branching:**

| Candle Outcome | Action |
|----------------|--------|
| **SKIP** (no trade) | Set ALL THREE trade flags to `"No"`. **Skip Tasks 3–4, go directly to Task 5.** |
| **TRADE** (executed) | Set `orb_candle_has_trade = "Yes"`. Capture the **Broke Time** from the strategy report. **Proceed to Task 3.** |

**Capture Candle's entry time for downstream tasks:**

From the orb-strategy report table, extract the `Broke Time` value (format `HH:MM`).

Calculate the downstream `time` parameter:

```
entry_time   = Broke Time + sp.hour_diff hours
next_time    = entry_time + 2min
```

Example: `Broke Time = "09:36"`, `sp.hour_diff = 1` → `entry_time = "10:36"` → `next_time = "10:38"`

Store `next_time` for use in Tasks 3 and 4.

---

### Task 3 — FVG Strategy

Invoke the `orb-strategy` skill with FVG as the strategy variant, using the downstream time from Task 2:

```
orb-strategy:
  date:         <d.date>
  time:         <next_time>      (entry_time + 2min from Task 2)
  day:          <d.day>
  month:        <sp.month>
  orb_type:     "FVG"
  session_end:  <sp.session_end>
  hour_diff:    <sp.hour_diff>
```

**Determine outcome:**

The FVG strategy may **SKIP** for these reasons:
- No valid FVG Cover (value is `"-"` or `null`)
- No valid FVG TP (value is `"-"` or `null`)
- Other skip conditions

Watch for phrases like `"No valid FVG Cover"`, `"skipping FVG strategy"`, or general skip messages.

**Branching:**

| FVG Outcome | Action |
|-------------|--------|
| **SKIP** (no valid FVG Cover) | Set `orb_fvg_has_trade = "No"` **and** `orb_combined_has_trade = "No"`. **Skip Task 4, go directly to Task 5.** |
| **TRADE** (executed) | Set `orb_fvg_has_trade = "Yes"`. **Proceed to Task 4.** |

---

### Task 4 — Combined Strategy

Invoke the `orb-strategy` skill with Combined as the strategy variant, reusing the same downstream time:

```
orb-strategy:
  date:         <d.date>
  time:         <next_time>      (entry_time + 2min from Task 2)
  day:          <d.day>
  month:        <sp.month>
  orb_type:     "Combined"
  session_end:  <sp.session_end>
  hour_diff:    <sp.hour_diff>
```

If we reach this point, both Candle and FVG executed successfully — the Combined strategy can proceed.

Set `orb_combined_has_trade = "Yes"`.

**Proceed to Task 5.**

---

### Task 5 — Journal Record

Invoke the `orb-backtest-journal` skill with all current journal model values plus the current date:

```
orb-backtest-journal:
  date:                       <d.date>
  bank_holiday_labels:        <journal.bank_holiday_labels>
  high_impact_labels:         <journal.high_impact_labels>
  orb_candle_has_trade:       <journal.orb_candle_has_trade>
  orb_fvg_has_trade:          <journal.orb_fvg_has_trade>
  orb_combined_has_trade:     <journal.orb_combined_has_trade>
```

**If `orb-backtest-journal` fails:**
- Log the error: `"Journal creation failed for {d.date} — {error details}"`
- Continue to the state wipe and next date

---

### State Wipe

After Task 5 completes (success or failure), reset the journal model:

- Clear `orb_candle_has_trade`
- Clear `orb_fvg_has_trade`
- Clear `orb_combined_has_trade`
- Clear `bank_holiday_labels`
- Clear `high_impact_labels`

Continue to the next date in the inner loop. When all dates are exhausted, continue to the next session period in the outer loop.

---

### Per-Date Summary

After each date completes, display a summary table:

```
## ORB Orchestrator — {d.date} ({d.day})

| Step | Detail |
|------|--------|
| News | {bank_holiday_labels joined} / {high_impact_labels joined} |
| Candle | {Yes / No — if No, reason} |
| FVG | {Yes / No — if No, reason} |
| Combined | {Yes / No — if No, reason} |
| Journal | {Created / Failed} |
```

---

## Full Example

**Input:**

```json
[
  {
    "time": "10:35",
    "hour_diff": 1,
    "session_end": "13:00",
    "month": "June",
    "dates": [
      {"day": "Monday", "date": "01/06/2026"}
    ]
  }
]
```

### Date: Monday 01/06/2026

**Task 1 — Forex Factory:**
- `forex-factory-day-news("01/06/2026")`
- Returns: `bank_holidays: [{ "currency": "CHF", "event": "Bank Holiday" }]`, `high_impact_events: [{ "currency": "USD", "event": "ISM Manufacturing PMI" }]`
- `bank_holiday_labels = ["CHF - Bank Holiday"]`
- `high_impact_labels = ["USD - ISM Manufacturing PMI"]`

**Task 2 — Candle:**
- `orb-strategy(date="01/06/2026", time="10:35", day="Monday", month="June", orb_type="Candle", session_end="13:00", hour_diff=1)`
- Report: ORB broke at `09:37`, Candle TP hit → Win. Broke Time = `09:37`.
- `orb_candle_has_trade = "Yes"`
- `entry_time = "10:37"`, `next_time = "10:39"`

**Task 3 — FVG:**
- `orb-strategy(date="01/06/2026", time="10:39", day="Monday", month="June", orb_type="FVG", session_end="13:00", hour_diff=1)`
- Report: FVG Cover is `"-"` → SKIP.
- `orb_fvg_has_trade = "No"`, `orb_combined_has_trade = "No"`
- Jump to Task 5.

**Task 5 — Journal:**
- `orb-backtest-journal(date="01/06/2026", bank_holiday_labels=["CHF - Bank Holiday"], high_impact_labels=["USD - ISM Manufacturing PMI"], orb_candle_has_trade="Yes", orb_fvg_has_trade="No", orb_combined_has_trade="No")`
- Row created in Notion.

**Summary:**

```
## ORB Orchestrator — 01/06/2026 (Monday)

| Step | Detail |
|------|--------|
| News | CHF - Bank Holiday / USD - ISM Manufacturing PMI |
| Candle | Yes |
| FVG | No — no valid FVG Cover |
| Combined | No — skipped (FVG failed) |
| Journal | Created |
```

---

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| `session_periods` has more than 2 elements | Reject with error: `"Maximum 2 session periods allowed — received {count}."` |
| `dates` array is empty | Skip the object entirely, log `"No weekdays in {sp.month} period — skipping."` |
| `forex-factory-day-news` fails | Set both news arrays to `["N/A"]`, log warning, continue |
| `orb-strategy` Candle: ORB does not break | Mark all three trade flags `"No"`, jump to Task 5 |
| `orb-strategy` Candle: breaks outside session | Mark all three trade flags `"No"`, jump to Task 5 |
| `orb-strategy` Candle: unexpected error | Mark all three trade flags `"No"`, log error, jump to Task 5 |
| `orb-strategy` FVG: no valid FVG Cover / TP | Mark `fvg = "No"`, `combined = "No"`, jump to Task 5 |
| `orb-strategy` FVG: unexpected error | Mark `fvg = "No"`, `combined = "No"`, log error, jump to Task 5 |
| `orb-strategy` Combined: skip or error | Mark `combined = "No"`, proceed to Task 5 (Candle and FVG flags unchanged) |
| `orb-backtest-journal` fails | Log error, wipe state, continue to next date |
| Single-date input (one object, one date) | Runs Task 1–5 once and finishes |
| DST transition month (2 objects) | Each object iterates independently with its own `time`/`session_end` |
| `next_time` minutes overflow (e.g., `10:59` + 2min = `11:01`) | Compute correctly using hour-minute arithmetic |

---

## Strategy Execution Flow (Visual)

```
FOR EACH session_period IN session_periods
  time = sp.time
  hour_diff = sp.hour_diff
  session_end = sp.session_end
  month = sp.month

  FOR EACH date_entry IN sp.dates
    day  = date_entry.day
    date = date_entry.date

    ┌─ Task 1: forex-factory-day-news(date)
    │   → bank_holiday_labels, high_impact_labels
    │
    ├─ Task 2: orb-strategy(Candle, time, hour_diff)
    │   ├─ SKIP → candle=No, fvg=No, combined=No → Task 5 ─┐
    │   └─ TRADE → candle=Yes, capture next_time            │
    │       │                                                │
    │       ├─ Task 3: orb-strategy(FVG, next_time, hour_diff)
    │       │   ├─ SKIP → fvg=No, combined=No → Task 5 ─────┤
    │       │   └─ TRADE → fvg=Yes                           │
    │       │       │                                        │
    │       │       └─ Task 4: orb-strategy(Combined, next_time, hour_diff)
    │       │           └─ combined=Yes ──┐                  │
    │       │                             │                  │
    │       └─────────────────────────────┤                  │
    │                                     ↓                  │
    └─ Task 5: orb-backtest-journal(all values) ←───────────┘
        → WIPE journal model → NEXT date
```

## Guidelines

- The `session_periods` input matches `fetch-dates` output exactly — in future iterations the orchestrator will call `fetch-dates` internally
- `orb_candle_has_trade` is the master flag: if Candle fails, all three strategies are considered non-trade for that date
- `orb_fvg_has_trade` failure cascades to `orb_combined_has_trade` but does NOT affect `orb_candle_has_trade`
- `next_time` is derived only from Candle's Broke Time — FVG and Combined reuse the same entry window since the ORB breaks once per session
- Journal model is ephemeral: cleared after each date to prevent cross-contamination
- All three `orb-strategy` calls use the same `date`, `day`, `month`, `session_end`, and `hour_diff` — only `orb_type` and `time` vary
- The orchestrator skill has no scripts — it relies entirely on the AI agent following these instructions to invoke other skills
