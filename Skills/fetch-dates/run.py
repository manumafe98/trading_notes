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


def find_nth_sunday(year: int, month: int, n: int):
    """Return the day-of-month of the nth Sunday in the given month/year."""
    cal = calendar.monthcalendar(year, month)
    count = 0
    for week in cal:
        sunday = week[calendar.SUNDAY]
        if sunday != 0:
            count += 1
            if count == n:
                return sunday
    return None


def get_month_dates_with_dst(month_num: int, year: int):
    month_name = calendar.month_name[month_num]
    _, num_days = calendar.monthrange(year, month_num)

    cal = calendar.monthcalendar(year, month_num)
    all_weekdays = []
    for week in cal:
        for dow, day in enumerate(week):
            if day == 0:
                continue
            if dow not in (calendar.SATURDAY, calendar.SUNDAY):
                all_weekdays.append({
                    "day_num": day,
                    "day_name": calendar.day_name[dow],
                    "date_str": f"{day:02d}/{month_num:02d}/{year}",
                })

    if month_num == 3:
        transition = find_nth_sunday(year, 3, 2)
        periods = [
            ("11:35", "14:00", 1, transition - 1),
            ("10:35", "13:00", transition, num_days),
        ]
    elif month_num == 11:
        transition = find_nth_sunday(year, 11, 1)
        periods = [
            ("10:35", "13:00", 1, transition - 1),
            ("11:35", "14:00", transition, num_days),
        ]
    elif 4 <= month_num <= 10:
        periods = [("10:35", "13:00", 1, num_days)]
    else:
        periods = [("11:35", "14:00", 1, num_days)]

    result = []
    for time_val, session_val, start_day, end_day in periods:
        dates = [
            {"day": wd["day_name"], "date": wd["date_str"]}
            for wd in all_weekdays
            if start_day <= wd["day_num"] <= end_day
        ]
        if dates:
            result.append({
                "time": time_val,
                "session_end": session_val,
                "month": month_name,
                "dates": dates,
            })

    return result


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

    result = get_month_dates_with_dst(month_num, year)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
