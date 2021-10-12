from datetime import datetime
import pytz


class ServerTime:
    def __init__(self, datetime_string: str, timezone: str = "UTC"):
        self.datetime = self.convert_datetime(datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S.%f"))
        self.year = self.datetime.year
        self.month = self.datetime.month
        self.week = self.datetime.week
        self.day = self.datetime.day
        self.hour = self.datetime.hour
        self.minute = self.datetime.minute
        self.second = self.datetime.second

    def __repr__(self):
        return self.datetime

    def __add__(self, datetime_object):
        return self.datetime + datetime_object

    def __sub__(self, datetime_object):
        return self.datetime - datetime_object

    def __lt__(self, datetime_object):
        return self.datetime < datetime_object

    def __le__(self, datetime_object):
        return self.datetime <= datetime_object

    def __gt__(self, datetime_object):
        return self.datetime > datetime_object

    def __ge__(self, datetime_object):
        return self.datetime >= datetime_object

    def __eq__(self, datetime_object):
        return self.datetime == datetime_object

    def __ne__(self, datetime_object):
        return self.datetime != datetime_object

    def convert_datetime(self, datetime):
        return pytz.timezone(self.timezone).localize(datetime)


