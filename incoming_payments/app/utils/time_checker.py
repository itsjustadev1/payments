from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

current_time = datetime.utcnow()

six_months_ago = current_time - relativedelta(months=6)
one_year_ago = current_time - relativedelta(months=12)


def convert_to_utc_format(date_str):
    if "+00:00" in date_str or "-00:00" in date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")
        dt_utc = dt.astimezone(tz=None).replace(tzinfo=None)
    elif date_str.endswith("Z"):
        dt_utc = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        raise ValueError(f"Unsupported date format: {date_str}")
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def convert_to_datetime(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            final_string = convert_to_utc_format(date_str)
            return datetime.strptime(final_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date_str}") from e
