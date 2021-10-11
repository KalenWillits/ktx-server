from datetime import datetime
import pytz


TIMEZONE = "UTC"

def convert_datetime():
    return pytz.timezone(TIMEZONE).localize(datetime.utcnow())


class ServerTime:
    def __init__(self, datetime_string: str):
        self.datetime = convertdatetime(datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S"))

    def __repr__(self):
        return self.datetime

    def convert_datetime(datetime):
        return pytz.timezone(TIMEZONE).localize(datetime)


