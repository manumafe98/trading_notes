import sys
import os
import json
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from Skills._shared.forex_factory import (
    init_session,
    parse_date,
    validate_date,
    fetch_forex_factory_calendar,
    parse_embedded_calendar
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def filter_bank_holiday(event_data):
    return "bank holiday" in event_data["event"].lower()


def main():
    init_session()

    if len(sys.argv) < 2:
        print(json.dumps({"error": "No date provided"}))
        return

    date_input = " ".join(sys.argv[1:])

    date_obj = parse_date(date_input)
    valid, error = validate_date(date_obj)

    if not valid:
        print(json.dumps({"error": error}))
        return

    html = fetch_forex_factory_calendar(date_obj)
    result = parse_embedded_calendar(html, date_obj, event_filter=filter_bank_holiday)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()