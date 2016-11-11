from moviepy import audio


class AudioInfo:
    @property
    def mp3(self):
        return self.mp3

    @mp3.setter
    def mp3(self, value):
        self.mp3 = value

    def __init__(self, pathToMp3):
        pass

    def get_duration(self):
        return 213
