---
name: forex-factory-bank-holiday-fetch
description: >
  Checks if a given date is a US bank holiday by scraping Forex Factory's
  calendar. Use this skill when the user asks whether markets are closed,
  if there's a bank holiday, or whether a specific date is a trading holiday.
---

# Forex Factory Bank Holiday Fetch

Checks whether a given date is a US bank holiday by looking for bank holiday events on Forex Factory's calendar.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | string | yes | Date in `dd/mm/yyyy` format or natural language like `"1st of May 2025"` |

## Instructions

1. Run the Python script located at `Skills/forex_factory_bank_holiday_fetch/run.py` with the date as argument:

```bash
python Skills/forex_factory_bank_holiday_fetch/run.py <date>
```

2. The script will:
   - Parse the date (supports multiple formats including natural language)
   - Fetch the Forex Factory calendar page for that date
   - Filter for events containing "bank holiday" in the name
   - Return a JSON object with `date` and `events` array

3. If the `events` array is empty, the date is **not** a bank holiday. Otherwise, present the holiday details.

## Examples

- "Is May 26th 2025 a bank holiday?"
- "Are markets closed on 04/07/2025?"
- "Check if there's a trading holiday on January 1st 2026"
