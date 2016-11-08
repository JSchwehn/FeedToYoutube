import re

class Chapter:
    """Represents a chapter entry"""

    def __init__(self, timestamp, title, separator=" - "):
        self.timestamp = timestamp
        self.title = title
        self.separator = separator

    @property
    def timestamp(self):
        return self.timestamp

    @timestamp.setter
    def timestamp(self, value):
        self.timestamp = value

    @property
    def title(self):

        return self.title

    @title.setter
    def title(self, value):
        self.title = value

    @property
    def separator(self):
        return self.separator

    @separator.setter
    def separator(self, value):
        self.separator = value

    def toString(self):
        tmp = self.timestamp.split('.')
        return tmp[0] + self.separator + self.title
