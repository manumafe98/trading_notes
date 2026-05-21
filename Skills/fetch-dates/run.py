import sys
import json
import calendar
from datetime import datetime


def parse_month(month_str: str):
    try:
        return datetime.strptime(month_str, "%B").month
    except ValueError:
        return None


def parse_year(year_str: str):
    try:
        year = int(year_str)
        if year < 1:
            return None
        return year
    except ValueError:
        return None


def get_weekdays(month_num: int, year: int):
    cal = calendar.monthcalendar(year, month_num)
    results = []

    for week in cal:
        for dow, day in enumerate(week):
            if day == 0:
                continue
            if dow not in (5, 6):  # Exclude Saturday=5, Sunday=6
                day_name = calendar.day_name[dow]
                date_str = f"{day:02d}/{month_num:02d}/{year}"
                results.append({"Day": day_name, "Date": date_str})

    return results


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: python run.py <month> <year>"}))
        return

    month_str = sys.argv[1]
    year_str = sys.argv[2]

    month_num = parse_month(month_str)
    if month_num is None:
        print(json.dumps({"error": f"Invalid month: {month_str}"}))
        return

    year = parse_year(year_str)
    if year is None:
        print(json.dumps({"error": f"Invalid year: {year_str}"}))
        return

    weekdays = get_weekdays(month_num, year)
    print(json.dumps(weekdays, indent=2))


if __name__ == "__main__":
    main()
