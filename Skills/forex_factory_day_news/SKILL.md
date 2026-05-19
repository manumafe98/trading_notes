---
name: forex-factory-day-news
description: >
  Fetches both US bank holidays and USD high-impact economic events from Forex
  Factory for a specific date. High-impact events are filtered to Argentina
  business hours (10:30-13:00 Mar-Nov, 11:30-14:00 Dec-Feb). Use this skill
  when the user asks about a trading day's events, whether markets are closed,
  bank holidays, or high-impact USD news for a given date.
---

# Forex Factory Day News

Fetches a daily summary from Forex Factory: US bank holidays and USD high-impact economic events within Argentina business hours.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | string | yes | Date in `dd/mm/yyyy`, `yyyy-mm-dd`, or natural language like `"1st of May 2025"` |

## Instructions

1. Run the script with the date:

```bash
python run.py <date>
```

The script is in the same folder as this SKILL.md. Use the full path to `run.py` when running from outside the skill folder.

2. The script outputs JSON with three keys:
   - `date` — the parsed date in `YYYY-MM-DD` format
   - `bank_holidays` — array of US bank holiday events (empty if none)
   - `high_impact_events` — array of USD high-impact events within Argentina business hours (empty if none)

### Output Format

Each event object:

```json
{
  "event": "ISM Services PMI",
  "currency": "USD",
  "time": "11:00am",
  "impact": "high"
}
```

Full output:

```json
{
  "date": "2026-04-06",
  "bank_holidays": [
    {
      "event": "Bank Holiday",
      "currency": "CHF",
      "time": "All Day",
      "impact": "holiday"
    },
    {
      "event": "French Bank Holiday",
      "currency": "EUR",
      "time": "All Day",
      "impact": "holiday"
    }
  ],
  "high_impact_events": [
    {
      "event": "ISM Services PMI",
      "currency": "USD",
      "time": "11:00am",
      "impact": "high"
    }
  ]
}
```

### Presenting Results to the User

Display bank holidays and high-impact events in separate tables. Both tables use `Time | Currency | Event`.

**When events exist:**

```
## Forex Factory — Mon Apr 6, 2026

**Bank Holidays**
| Time | Currency | Event |
|------|----------|-------|
| All Day | CHF | Bank Holiday |
| All Day | EUR | French Bank Holiday |
| All Day | EUR | German Bank Holiday |
| All Day | EUR | Italian Bank Holiday |
| All Day | GBP | Bank Holiday |

**USD High Impact Events** (Argentina hours)
| Time | Currency | Event |
|------|----------|-------|
| 11:00am | USD | ISM Services PMI |
```

**When nothing found:**

```
## Forex Factory — Sat May 17, 2025

No US bank holidays or USD high-impact events for this date.
```
## Forex Factory — Mon Apr 6, 2026

| Time | Currency | Event | Forecast | Actual |
|------|----------|-------|----------|--------|
| All Day | CHF | Bank Holiday | — | — |
| All Day | EUR | French Bank Holiday | — | — |
| All Day | EUR | German Bank Holiday | — | — |
| All Day | EUR | Italian Bank Holiday | — | — |
| All Day | GBP | Bank Holiday | — | — |
| 11:00am | USD | ISM Services PMI | 54.8 | 54.0 |
```

(Argentina business hours filter applied to high-impact events: 10:30–13:00 or 11:30–14:00)

**When nothing found:**

```
## Forex Factory — Sat May 17, 2025

No US bank holidays or USD high-impact events for this date.
```

### Edge Cases

- **Future dates**: Script returns error `"Date cannot be in the future"`
- **Weekend dates**: Typically return empty arrays — present as "no events"
- **DST transitions**: Argentina business hours adjust automatically by month (Mar–Nov vs Dec–Feb)

## Dependencies

```
requests
```

Install with: `pip install requests`

## Usage Examples

- "What's happening on the 1st of May 2025?"
- "Are markets closed on 04/07/2025?"
- "What USD news is there on 15/05/2025?"
- "Check if December 25th 2025 is a bank holiday"
- "Fetch forex factory events for 2025-06-02"
