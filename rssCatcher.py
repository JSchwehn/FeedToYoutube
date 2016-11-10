import sqlite3
import feedparser
import datetime
from feed import Feed
from episode import Episode
from chapter import Chapter
from hashlib import md5


class RssCatcher:
    db = None
    table_feed = "feeds"
    table_episodes = "episodes"
    table_chapters = "chapters"
    config = None
    feed = None
    feed_url = None

    def __init__(self, config):
        self.config = config
        self.init_db()

    def load_rss(self, feedUrl):
        self.feed_url = feedUrl
        print "Loading RSS Feed: " + self.feed_url
        f = feedparser.parse(self.feed_url)
        if not hasattr(f, "etag"):
            etag = f.feed.updated
        else:
            etag = f.etag
        if not self._feed_has_changed(etag):
            print "Nothing has changed"
            return {'status': "304", "message": "Not Modified"}
        if not hasattr(f.feed, "updated"):
            f.feed.updated = unicode(datetime.datetime.now())
        imageUrl = ""
        if hasattr(f.feed, 'image') and hasattr(f.feed.image, "href"):
            imageUrl = f.feed.image.href
        feed = Feed(feedUrl,
                    image=imageUrl,
                    etag=etag,
                    subtitle=f.feed.summary,
                    title=f.feed.title,
                    updated=f.feed.updated)
        self.save_feed(feed)
        feed.episodes = []

        print "Importing " + feed.title
        for episode in f.entries:
            print " Episode " + episode.title
            if self._is_known_episode(episode):
                continue

            # chapter handling
            cs = []
            if hasattr(episode, "psc_chapters"):
                for chapter in episode.psc_chapters.chapters:
                    link = ""
                    image = ""
                    if hasattr(chapter, 'href'):
                        link = chapter.href
                    if hasattr(chapter, 'image'):
                        image = chapter.image

                    c = Chapter(
                        start=chapter.start,
                        image=image,
                        href=link,
                        title=chapter.title)
                    print "\t" + c.start + ": " + c.title + " Image= " + c.image + " Href= " + c.href
                    cs.append(c)
            image = ""
            if hasattr(episode, 'image') and hasattr(episode.image, "href"):
                image = episode.image.href
            e = Episode(feed_id=feed.feed_id,
                        rss_episode_id=episode.id,
                        duration=episode.itunes_duration,
                        link=episode.link,
                        title=episode.title,
                        subtitle=episode.subtitle,
                        description=episode.summary,
                        published=episode.published,
                        chapters=cs,
                        image=image
                        )
            self._insert_episode(e)
            if hasattr(feed.episodes, 'append'):
                feed.episodes.append(e)
        self.feed = feed
        return self.feed

    def init_db(self):
        self.db = sqlite3.connect(self.config.db_name)
        self._create_tables()

    def close_db(self):
        self.db.close()

    def save_episode(self, episode):
        if episode.episode_id == "" or episode.episode_id is None:
            return self._insert_episode(episode)

    def save_feed(self, feed):
        if feed.feed_id == "" or feed.feed_id is None:
            return self._insert_feed(feed)

    def _insert_feed(self, feed):
        sql = "INSERT INTO " + self.table_feed + \
              " (url, etag, title, subtitle, image, updated)" + \
              " VALUES (?, ?, ?, ?, ?, ?)"
        cur = self.db.cursor()
        cur.execute(sql, [feed.url, feed.etag, feed.title, feed.subtitle, str(feed.image), feed.updated])
        feed.feed_id = cur.lastrowid
        self.db.commit()

    def _insert_episode(self, episode):
        sql = "INSERT INTO " + self.table_episodes + " (rss_feed_id, " \
                                                     "rss_episode_id, " \
                                                     "duration, " \
                                                     "title, " \
                                                     "description, " \
                                                     "subtitle, " \
                                                     "link, " \
                                                     "published, " \
                                                     "image " \
                                                     ") VALUES (?,?,?,?,?,?,?,?,?)"
        cur = self.db.cursor()
        cur.execute(sql, [episode.feed_id, episode.rss_episode_id, episode.duration, episode.title, episode.description,
                          episode.subtitle, episode.link, episode.published, episode.image])
        episode.episode_id = cur.lastrowid
        self.db.commit()
        self._insert_chapters(episode)

    def _insert_chapters(self, episode):
        sql = "INSERT INTO " + self.table_chapters + \
              "(episode_id,start, title, image, href) VALUES (?,?,?,?,?)"
        cur = self.db.cursor()
        for chapter in episode.chapters:
            cur.execute(sql, [episode.episode_id, chapter.start, chapter.title, chapter.image, chapter.href])
        self.db.commit()

    def _update_episode(self, episode):
        sql = "UPDATE"

    def _update_feed(self, feed):
        if feed.id == "" or feed.id is None:
            raise RuntimeWarning("Can't update because no id found")
        sql = "UPDATE"

    def _create_tables(self):
        sql = 'CREATE TABLE IF NOT EXISTS ' + self.table_feed + \
              ' ( id INTEGER PRIMARY KEY AUTOINCREMENT,  ' \
              'url VARCHAR UNIQUE, ' \
              'etag VARCHAR, ' \
              'title VARCHAR,  ' \
              'image BLOB,  ' \
              'subtitle VARCHAR,  ' \
              'updated DATE);'
        cur = self.db.cursor()
        cur.execute(sql)
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS `etag_idx` ON `" + self.table_feed + "` (`etag` )")
        cur.execute("CREATE INDEX IF NOT EXISTS `id_idx` ON `" + self.table_feed + "` (`id` )")
        sql = 'CREATE TABLE IF NOT EXISTS ' + self.table_episodes + \
              ' ( id INTEGER PRIMARY KEY AUTOINCREMENT,  ' \
              'rss_feed_id VARCHAR, ' \
              'rss_episode_id VARCHAR NOT NULL, ' \
              'title VARCHAR, ' \
              'subtitle VARCHAR, ' \
              'description BLOB, ' \
              'image BLOB, ' \
              'duration VARCHAR, link VARCHAR, chapters TEXT ,' \
              'published DATE, ' \
              'youtube_upload_date DATE);'
        cur.execute(sql)
        sql = """
        CREATE TABLE IF NOT EXISTS `chapters` (
            `id` INTEGER NOT NULL,
            `episode_id` INTEGER NOT NULL,
            `title` TEXT,
            `start`	TEXT,
            `image`	BLOB,
            `href` TEXT,
            PRIMARY KEY(`id`)
        );
        """
        cur.execute(sql)
        sql = "CREATE INDEX IF NOT EXISTS `eid_idx` ON `chapters` (`episode_id` );"
        cur.execute(sql)

    def _feed_has_changed(self, etag):
        cur = self.db.cursor()
        cur.execute("SELECT etag FROM " + self.table_feed + " WHERE etag = ?", [etag])
        data = cur.fetchall()
        if len(data) > 0:
            return False
        else:
            return True

    def _is_known_episode(self, episode):
        return False
