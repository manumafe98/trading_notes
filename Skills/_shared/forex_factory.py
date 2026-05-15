import re
import time
import json
import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any

import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

SESSION = requests.Session()

SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36"
    )
})

MAX_RETRIES = 3
RETRY_DELAY_BASE = 2


def init_session():
    SESSION.get("https://www.forexfactory.com/", timeout=30)


def parse_date(date_str: str) -> Optional[datetime]:
    date_str = date_str.strip()

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d %B %Y",
        "%d %b %Y",
        "%B %d, %Y",
        "%b %d, %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    natural_patterns = [
        r"(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?(\w+)\s+(\d{4})",
        r"(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})",
    ]

    for pattern in natural_patterns:
        match = re.match(pattern, date_str, re.IGNORECASE)

        if match:
            parts = match.groups()

            if parts[0].isdigit():
                day = int(parts[0])
                month_str = parts[1]
                year = int(parts[2])
            else:
                month_str = parts[0]
                day = int(parts[1])
                year = int(parts[2])

            try:
                month = datetime.strptime(month_str[:3], "%b").month
                return datetime(year, month, day)

            except ValueError:
                try:
                    month = datetime.strptime(month_str, "%B").month
                    return datetime(year, month, day)

                except ValueError:
                    pass

    return None


def validate_date(date_obj: Optional[datetime]) -> Tuple[bool, Optional[str]]:

    if date_obj is None:
        return False, "Invalid date format"

    if date_obj > datetime.now():
        return False, "Date cannot be in the future"

    return True, None


def fetch_calendar(url: str, retries: int = MAX_RETRIES) -> str:

    for attempt in range(retries):

        try:
            response = SESSION.get(url, timeout=30)
            response.raise_for_status()

            return response.text

        except requests.exceptions.HTTPError as e:

            if e.response.status_code in (429, 503):

                wait_time = RETRY_DELAY_BASE ** attempt

                logger.warning(
                    f"Rate limited, waiting {wait_time}s "
                    f"before retry {attempt + 1}/{retries}"
                )

                time.sleep(wait_time)

            else:
                logger.error(f"HTTP error: {e}")
                raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    return f"Error fetching calendar after {retries} attempts"


def fetch_forex_factory_calendar(date_obj: datetime) -> str:

    formatted_date = date_obj.strftime("%b%d.%Y").lower()

    url = f"https://www.forexfactory.com/calendar?day={formatted_date}"

    logger.info(f"Fetching: {url}")

    return fetch_calendar(url)


def parse_embedded_calendar(
    html: str,
    date_obj: datetime,
    event_filter: Optional[callable] = None
) -> Dict[str, Any]:

    if html.startswith("Error"):
        return {"error": html}

    # Find event-like JSON objects
    event_matches = re.findall(
        r'\{.*?"name":"[^"]+".*?"currency":"[^"]+".*?\}',
        html,
        re.DOTALL
    )

    if not event_matches:
        return {"error": "Could not locate event objects"}

    result_events = []
    seen = set()

    for raw_event in event_matches:

        try:
            event = json.loads(raw_event)

        except Exception:
            continue

        event_data = {
            "event": event.get("name", ""),
            "currency": event.get("currency", ""),
            "time": event.get("timeLabel", ""),
            "impact": event.get("impactName", "").lower(),
            "actual": event.get("actual", ""),
            "forecast": event.get("forecast", "")
        }

        if not event_data["event"]:
            continue

        event_key = (
            event_data["event"],
            event_data["currency"],
            event_data["time"],
            event_data["impact"]
        )

        if event_key in seen:
            continue

        seen.add(event_key)

        if event_filter is None or event_filter(event_data):
            result_events.append(event_data)

    return {
        "date": date_obj.strftime("%Y-%m-%d"),
        "events": result_events
    }


def parse_time_string(time_str: str) -> Tuple[int, int, bool]:

    lowered = time_str.lower().strip()

    is_pm = "pm" in lowered

    cleaned = (
        lowered
        .replace("am", "")
        .replace("pm", "")
        .strip()
    )

    if not cleaned.replace(":", "").isdigit():
        raise ValueError(f"Invalid time format: {time_str}")

    parts = cleaned.split(":")

    hour = int(parts[0])

    minute = int(parts[1]) if len(parts) > 1 else 0

    if is_pm and hour != 12:
        hour += 12

    elif not is_pm and hour == 12:
        hour = 0

    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        raise ValueError(f"Time out of range: {hour}:{minute}")

    return hour, minute, is_pm


def filter_by_time_range(
    events: List[Dict],
    start_hour: int,
    start_minute: int,
    end_hour: int,
    end_minute: int
) -> List[Dict]:

    start_minutes = start_hour * 60 + start_minute
    end_minutes = end_hour * 60 + end_minute

    filtered = []

    for event in events:

        time_str = event.get("time", "")

        if not time_str:
            continue

        try:
            hour, minute, _ = parse_time_string(time_str)

            event_minutes = hour * 60 + minute

            if start_minutes <= event_minutes < end_minutes:
                filtered.append(event)

        except ValueError:
            logger.warning(f"Skipping invalid time: {time_str}")
            continue

    return filtered