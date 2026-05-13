import sys
import os
import json
import logging
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from Skills._shared.forex_factory import (
    init_session,
    parse_date,
    validate_date,
    fetch_forex_factory_calendar,
    parse_embedded_calendar,
    filter_by_time_range
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def filter_high_impact(event_data):
    return event_data["currency"] == "USD" and event_data["impact"] == "high"


def filter_argentina_business_hours(events, date_obj):
    month = date_obj.month

    if 3 <= month <= 11:
        start_hour, start_minute = 10, 30
        end_hour, end_minute = 13, 0
    else:
        start_hour, start_minute = 11, 30
        end_hour, end_minute = 14, 0

    return filter_by_time_range(events, start_hour, start_minute, end_hour, end_minute)


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
    result = parse_embedded_calendar(html, date_obj, event_filter=filter_high_impact)

    if "error" in result:
        print(json.dumps(result))
        return

    filtered_events = filter_argentina_business_hours(result["events"], date_obj)

    print(json.dumps({"date": result["date"], "events": filtered_events}, indent=2))


if __name__ == "__main__":
    main()