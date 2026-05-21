---
name: fetch-dates
description: >
  Fetches all weekday dates (Monday through Friday) for a given month and year,
  excluding Saturdays and Sundays. Returns a JSON array of objects with day name
  and date in dd/mm/yyyy format. Use this skill when the user asks for trading
  days, weekdays in a specific month, or needs a calendar of business days
  excluding weekends.
---

# Fetch Dates

Given a month name and year, returns all weekdays (Monday–Friday, excluding weekends) in that month as a JSON array.

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

2. The script outputs a JSON array of weekday date objects (Saturdays and Sundays excluded):

### Output Format

```json
[
  {"Day": "Thursday", "Date": "01/05/2025"},
  {"Day": "Friday",   "Date": "02/05/2025"},
  {"Day": "Monday",   "Date": "05/05/2025"},
  {"Day": "Tuesday",  "Date": "06/05/2025"}
]
```

Each object:
- `Day` — full weekday name (`"Monday"` through `"Friday"`)
- `Date` — date in `dd/mm/yyyy` format

### Presenting Results to the User

Display the weekdays in a table:

```
## Weekdays in May 2025

| Day       | Date       |
|-----------|------------|
| Thursday  | 01/05/2025 |
| Friday    | 02/05/2025 |
| Monday    | 05/05/2025 |
| Tuesday   | 06/05/2025 |
| Wednesday | 07/05/2025 |
| Thursday  | 08/05/2025 |
| Friday    | 09/05/2025 |
| ...       | ...        |
```

### Edge Cases

- **Invalid month**: Returns `{"error": "Invalid month: MonthName"}`
- **Invalid year**: Returns `{"error": "Invalid year: not_a_number"}`

## Dependencies

None — uses only Python standard library (`calendar`, `datetime`, `sys`, `json`).

## Usage Examples

- "Get weekdays in May 2025"
- "What are the trading days of January 2026?"
- "Fetch business days for December 2025 (excluding weekends)"
- "List all Mondays through Fridays in March 2025"
- "Weekdays in August 2025"
