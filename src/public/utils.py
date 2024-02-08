import datetime
from datetime import date


def get_datetime():
    """
    Return list [date, time]
    """
    date_now = date.today()
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    return [date_now, time_now]
