import re
import time
import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
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
            if len(parts) == 3:
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
                logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}/{retries}")
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


def parse_embedded_calendar(html: str, date_obj: datetime, event_filter: Optional[callable] = None) -> Dict[str, Any]:
    if html.startswith("Error"):
        return {"error": html}

    match = re.search(r'window\.calendarComponentStates\[\d+\]\s*=\s*\{', html)
    if not match:
        return {"error": "Could not find calendar data in page"}

    start_idx = match.start()
    brace_count = 0
    end_idx = start_idx

    for i in range(start_idx, len(html)):
        if html[i] == '{':
            brace_count += 1
        elif html[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break

    if end_idx <= start_idx:
        return {"error": "Could not parse calendar data"}

    data_block = html[start_idx:end_idx]

    events = re.findall(
        r'"name":"([^"]+)".*?"currency":"([^"]+)".*?"timeLabel":"([^"]+)".*?"impactName":"([^"]+)".*?"actual":"([^"]*)".*?"forecast":"([^"]*)"',
        data_block,
        re.DOTALL
    )

    result_events = []
    for match in events:
        name, currency, time_label, impact, actual, forecast = match

        event_data = {
            "event": name,
            "currency": currency,
            "time": time_label,
            "impact": impact,
            "actual": actual,
            "forecast": forecast
        }

        if event_filter is None or event_filter(event_data):
            result_events.append(event_data)

    return {"date": date_obj.strftime("%Y-%m-%d"), "events": result_events}


def parse_time_string(time_str: str) -> Tuple[int, int, bool]:
    time_str = time_str.lower().replace("am", "").replace("pm", "").strip()

    if not time_str.replace(":", "").isdigit():
        raise ValueError(f"Invalid time format: {time_str}")

    parts = time_str.split(":")
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0
    is_pm = "pm" in time_str.lower()

    if is_pm and hour != 12:
        hour += 12
    elif not is_pm and hour == 12:
        hour = 0

    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        raise ValueError(f"Time out of range: {hour}:{minute}")

    return hour, minute, is_pm


def filter_by_time_range(events: List[Dict], start_hour: int, start_minute: int, end_hour: int, end_minute: int) -> List[Dict]:
    start_minutes = start_hour * 60 + start_minute
    end_minutes = end_hour * 60 + end_minute

    filtered = []
    for event in events:
        time_str = event.get("time", "").lower().replace("am", "").replace("pm", "").strip()
        if not time_str.replace(":", "").isdigit():
            continue
        try:
            hour, minute, _ = parse_time_string(event["time"])
            event_minutes = hour * 60 + minute
            if start_minutes <= event_minutes < end_minutes:
                filtered.append(event)
        except ValueError:
            continue

    return filtered