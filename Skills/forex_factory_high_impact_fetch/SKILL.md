---
name: forex-factory-high-impact-fetch
description: >
  Fetches USD high impact news from Forex Factory for a specific date, filtered
  by Argentina business hours (10:30-13 or 11:30-14 depending on DST). Use this
  skill when the user asks about upcoming or past high-impact economic events,
  USD news releases, or Forex Factory calendar data for a given date.
---

# Forex Factory High Impact Fetch

Fetches USD high-impact economic events from Forex Factory for a specific date, filtered to Argentina business hours.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | string | yes | Date in `dd/mm/yyyy` format or natural language like `"1st of May 2025"` |

## Instructions

1. Run the Python script located at `Skills/forex_factory_high_impact_fetch/run.py` with the date as argument:

```bash
python Skills/forex_factory_high_impact_fetch/run.py <date>
```

2. The script will:
   - Parse the date (supports multiple formats including natural language)
   - Fetch the Forex Factory calendar page for that date
   - Filter for USD high-impact events only
   - Further filter by Argentina business hours (10:30–13:00 or 11:30–14:00 depending on DST)
   - Return a JSON object with `date` and `events` array

3. Present the results to the user.

## Dependencies

Requires packages listed in `Skills/forex_factory_high_impact_fetch/requirements.txt`:
- `requests`
- `beautifulsoup4`

## Examples

- "What high impact news is there on 14/05/2025?"
- "Fetch USD events for May 1st 2025"
- "Any important economic releases on 1st of May 2025?"
