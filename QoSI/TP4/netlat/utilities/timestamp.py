import requests
from datetime import datetime
import json


"""
{"timezone":"UTC","formatted":"16.04.2024 22:26","timestamp":1713306366007,"weekDay":2,"day":16,"month":4,"year":2024,"hour":22,"minute":26}
"""

class Timestamp:
    def __init__(self):
        self.url = "https://tools.aimylogic.com/api/now"
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                self.success = True
                data = response.json()
                for key, value in data.items():
                    setattr(self, key, value)
            else:
                self.success = False
        except Exception as e:
            self.success = False

    def __str__(self):
        str = ""
        if self.success:
            for key, value in self.__dict__.items():
                str += f"{key}: {value}\n"
        else:
            str = "Failed to get the timestamp"
        return str


    @staticmethod
    def get_timestamp():
        t = Timestamp()
        if t.success:
            return t.timestamp
        else:
            raise Exception("Failed to get the timestamp")

    @staticmethod
    def get_formatted():
        t = Timestamp()
        if t.success:
            return t.formatted
        else:
            raise Exception("Failed to get the formated date")

    @staticmethod
    def get_epoch():
        t = Timestamp()
        if t.success:
            return t.timestamp
        else:
            raise Exception("Failed to get the epoch")

    @staticmethod
    def get_weekday():
        t = Timestamp()
        if t.success:
            return t.weekDay
        else:
            raise Exception("Failed to get the weekday")

    @staticmethod
    def get_day():
        t = Timestamp()
        if t.success:
            return t.day
        else:
            raise Exception("Failed to get the day")

    @staticmethod
    def get_month():
        t = Timestamp()
        if t.success:
            return t.month
        else:
            raise Exception("Failed to get the month")

    @staticmethod
    def get_year():
        t = Timestamp()
        if t.success:
            return t.year
        else:
            raise Exception("Failed to get the year")
