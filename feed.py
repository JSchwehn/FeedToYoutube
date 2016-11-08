class Feed:
    def __init__(self, feed_id="",etag="",subtitle="", title="", updated=None):
        self.etag = etag
        self.title = title
        self.updated = updated
        self.subtitle = subtitle
        self.feed_id = feed_id

    @property
    def feed_id(self):
        return self.id

    @feed_id.setter
    def feed_id(self, value):
        self.id = value

    @property
    def etag(self):
        return self.etag

    @etag.setter
    def etag(self, value):
        self.etag = value

    @property
    def title(self):
        return self.title

    @title.setter
    def title(self, value):
        self.title = value

    @property
    def updated(self):
        return self.updated

    @updated.setter
    def updated(self, value):
        self.updated = value

    @property
    def episodes(self):
        return self.episodes

    @episodes.setter
    def episodes(self, value):
        if isinstance(value, list):
            self.episodes = value
        else:
            self.episodes = [value]

    @property
    def subtitle(self):
        return self.subtitle

    @subtitle.setter
    def subtitle(self, value):
        self.subtitle = value

