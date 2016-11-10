import re

class Chapter:
    """Represents a chapter entry"""

    def __init__(self, start, title, episode_id=None, image=None, href=None, chapter_id=None):
        self.start = start
        self.title = title
        self.image = image
        self.href = href
        self.chapter_id = chapter_id

    @property
    def chapter_id(self):
        return self.chapter_id

    @chapter_id.setter
    def chapter_id(self, value):
        self.chapter_id = value

    @property
    def href(self):
        return self.href

    @href.setter
    def href(self, value):
        self.href = value

    @property
    def image(self):
        return self.image

    @image.setter
    def image(self, value):
        self.image = value

    @property
    def start(self):
        return self.start

    @start.setter
    def start(self, value):
        self.start = value

    @property
    def title(self):
        return self.title

    @title.setter
    def title(self, value):
        self.title = value
