---
name: fetch-dates
description: >
  Fetches all weekday dates (Monday through Friday) for a given month and year,
  excluding Saturdays and Sundays. Returns a JSON array of DST-aware session
  groups, each with NY session times (adjusted for US DST) and the weekdays in
  that DST period. Use this skill when the user asks for trading days, weekdays
  in a specific month, or needs a calendar of business days excluding weekends.
---

# Fetch Dates

Given a month name and year, returns all weekdays (Monday–Friday, excluding weekends) grouped by US DST period with correct NY session times for Argentina business hours.

## Parameters

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| `month`   | string | yes      | Full month name in English (e.g., `"May"`, `"January"`, `"December"`) |
| `year`    | string | yes      | Year as a number (e.g., `"2025"`, `"2026"`) |

## Instructions

1. Run the script with month and year:

```bash
python run.py <month> <year>
```

The script is in the same folder as this SKILL.md. Use the full path to `run.py` when running from outside the skill folder.

2. The script outputs a JSON array of session-period objects, each containing the NY session times for that DST period and the weekdays within it:

### Output Format

```json
[
  {
    "time": "10:35",
    "session_end": "13:00",
    "month": "May",
    "dates": [
      {"day": "Monday",   "date": "04/05/2026"},
      {"day": "Tuesday",  "date": "05/05/2026"},
      {"day": "Wednesday","date": "06/05/2026"},
      {"day": "Thursday", "date": "07/05/2026"},
      {"day": "Friday",   "date": "08/05/2026"}
    ]
  }
]
```

Each object:
- `time` — NY session start in Argentina local time (`HH:MM`, 24h format)
- `session_end` — NY session end in Argentina local time (`HH:MM`, 24h format)
- `month` — full month name (same as input)
- `dates` — array of weekday objects (`day`: full weekday name, `date`: `dd/mm/yyyy`)

### DST Transition Months (March & November)

For March and November, the output may contain **two objects** — one for each DST period that falls within the month. The boundary is:

- **US DST starts**: second Sunday of March (spring forward)
- **US DST ends**: first Sunday of November (fall back)

**March example** (2026, second Sunday = March 8):

```json
[
  {
    "time": "11:35",
    "session_end": "14:00",
    "month": "March",
    "dates": [
      {"day": "Monday",   "date": "02/03/2026"},
      {"day": "Tuesday",  "date": "03/03/2026"},
      {"day": "Wednesday","date": "04/03/2026"},
      {"day": "Thursday", "date": "05/03/2026"},
      {"day": "Friday",   "date": "06/03/2026"}
    ]
  },
  {
    "time": "10:35",
    "session_end": "13:00",
    "month": "March",
    "dates": [
      {"day": "Monday",   "date": "09/03/2026"},
      {"day": "Tuesday",  "date": "10/03/2026"}
    ]
  }
]
```

### DST Session Times

| Months | US Timezone | `time` | `session_end` |
|--------|-------------|--------|---------------|
| April – October | EDT (DST) | `"10:35"` | `"13:00"` |
| December – February | EST (Standard) | `"11:35"` | `"14:00"` |
| March (before 2nd Sunday) | EST (Standard) | `"11:35"` | `"14:00"` |
| March (on/after 2nd Sunday) | EDT (DST) | `"10:35"` | `"13:00"` |
| November (before 1st Sunday) | EDT (DST) | `"10:35"` | `"13:00"` |
| November (on/after 1st Sunday) | EST (Standard) | `"11:35"` | `"14:00"` |

### Presenting Results to the User

Display each period as a group with its session times:

```
## Weekdays in March 2026

**Standard Time** (11:35–14:00):
| Day       | Date       |
|-----------|------------|
| Monday    | 02/03/2026 |
| Tuesday   | 03/03/2026 |
| Wednesday | 04/03/2026 |
| Thursday  | 05/03/2026 |
| Friday    | 06/03/2026 |

**DST** (10:35–13:00):
| Day       | Date       |
|-----------|------------|
| Monday    | 09/03/2026 |
| Tuesday   | 10/03/2026 |
| ...       | ...        |
```

For non-transition months, show a single group.

### Edge Cases

- **Invalid month**: Returns `{"error": "Invalid month: MonthName"}`
- **Invalid year**: Returns `{"error": "Invalid year: not_a_number"}`
- **Transition Sunday falls on day 1**: If the boundary Sunday is the 1st, there are no weekdays before it — only the "after" period is returned. Example: November 2026 (first Sunday = Nov 1) returns one object with standard time.
- **November with no weekdays before first Sunday**: If Nov 1 is a Saturday and Nov 2 is the first Sunday, the "before" period has no weekdays and is omitted. Example: November 2025.

## Dependencies

None — uses only Python standard library (`calendar`, `datetime`, `sys`, `json`).

## Usage Examples

- "Get weekdays in May 2025"
- "What are the trading days of January 2026?"
- "Fetch business days for December 2025 (excluding weekends)"
- "List all Mondays through Fridays in March 2025"
- "Weekdays in August 2025"
