from chapter import Chapter


class Episode:
    is_new = False

    @property
    def episode_id(self):
        return self.rss_episode_id

    @episode_id.setter
    def episode_id(self, value):
        self.rss_episode_id = value

    @property
    def rss_feed_id(self):
        return self.feed_id

    @rss_feed_id.setter
    def rss_feed_id(self, value):
        self.feed_id = value

    @rss_feed_id.deleter
    def rss_feed_id(self):
        del self.feed_id

    @property
    def rss_episode_id(self):
        return self.rss_episode_id

    @rss_episode_id.setter
    def rss_episode_id(self, value):
        self.rss_episode_id = value

    @property
    def title(self):
        return

    @title.setter
    def title(self, value):
        self.title = value

    @property
    def link(self):
        return self.link

    @link.setter
    def link(self, value):
        self.link = value

    @property
    def chapters(self):
        return self.chapters

    @chapters.setter
    def chapters(self, value):
        self.chapters = value

    @property
    def duration(self):
        return self.duration

    @duration.setter
    def duration(self, value):
        self.duration = value

    @property
    def description(self):
        return self.description

    @description.setter
    def description(self, value):
        self.description = value  #

    @property
    def subtitle(self):
        return self.subtitle

    @subtitle.setter
    def subtitle(self, value):
        self.subtitle = value

    @property
    def published(self):
        return self.published

    @published.setter
    def published(self, value):
        self.published = value

    @property
    def image(self):
        return self.image

    @image.setter
    def image(self, value):
        self.image = value

    def __init__(self,
                 episode_id=None,
                 feed_id="",
                 rss_episode_id="",
                 title="",
                 subtitle="",
                 description="",
                 published="",
                 duration="",
                 link="",
                 image="",
                 is_new=False,
                 chapters=[]):
        self.episode_id = episode_id,
        self.feed_id = feed_id
        self.rss_episode_id = rss_episode_id
        self.title = title
        self.link = link
        self.duration = duration
        self.subtitle = subtitle
        self.description = description
        self.published = published
        self.chapters = chapters
        self.image = image
        self.is_new = is_new
