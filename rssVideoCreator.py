import os.path
import configargparse
import sqlite3
import pprint as p
from hashlib import md5
import feedparser
from feed import Feed
from episode import Episode
from chapter import Chapter


class RssVideoCreator:
    config = None
    db = None
    table_feed = ""
    table_episodes = ""

    def __init__(self):
        self.load_config()
        self.init_db()
        self.load_rss()

    def load_config(self):
        p = configargparse.ArgParser(default_config_files=['./config.yaml'])
        p.add('-c', '--my-config', required=True, is_config_file=True, help='Config file path')
        p.add('-f', '--feed', help='URL to the atom feed')
        p.add('-vw', '--video-width', help='Video width in pixels')
        p.add('-vh', '--video-height', help='Video height in pixels')
        p.add('-vfps', '--video-fps', help='Video frames per seconds')
        p.add('-db', '--db-name', help='Name of the local feed database')
        p.add('-i', '--init', help='Imports feed with out any video processing and uploading')
        self.config = p.parse_args()

    def init_db(self):
        self.db = sqlite3.connect(self.config.db_name)
        tmp = md5(self.config.feed).hexdigest()
        self.table_feed = 'feed_' + tmp
        self.table_episodes = 'episodes_' + tmp
        self._create_tables()

    def load_rss(self):
        print "Loading RSS Feed"
        f = feedparser.parse(self.config.feed)
        if not self._feed_has_changed(f.etag):
            print "Nothing has changed"
            return {'status': "304", "message": "Not Modified"}

        feed = Feed(etag=f.etag,
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
            cs = []
            for chapter in episode.psc_chapters.chapters:
                c = Chapter(timestamp=chapter.start,
                            separator=" ",
                            title=chapter.title)
                cs.append(c)

            e = Episode(feed_id=feed.feed_id,
                        rss_episode_id=episode.id,
                        duration=episode.itunes_duration,
                        link=episode.link,
                        title=episode.title,
                        subtitle=episode.subtitle,
                        description=episode.summary,
                        published=episode.published,
                        chapters=cs
                        )
            self._insert_episode(e)

    def close_db(self):
        self.db.close()

    def save_episode(self, episode):
        if episode.episode_id == "" or episode.episode_id is None:
            return self._insert_episode(episode)

    def save_feed(self, feed):
        if feed.feed_id == "" or feed.feed_id is None:
            return self._insert_feed(feed)

    def _insert_episode(self, episode):
        chapter = ""
        for c in episode.chapters:
            chapter += c.toString() + "\n"

        sql = "INSERT INTO " + self.table_episodes + " (rss_feed_id, " \
                                                     "rss_episode_id, " \
                                                     "duration, " \
                                                     "title, " \
                                                     "description, " \
                                                     "subtitle, " \
                                                     "link, " \
                                                     "published, " \
                                                     "chapters" \
                                                     ") VALUES (?,?,?,?,?,?,?,?,?)"
        cur = self.db.cursor()
        cur.execute(sql, [episode.feed_id, episode.rss_episode_id,
                          episode.duration, episode.title,
                          episode.description, episode.subtitle,
                          episode.link, episode.published,
                          chapter
                          ])
        self.db.commit()

    def _update_episode(self, episode):
        sql = "UPDATE"

    def _insert_feed(self, feed):
        sql = "INSERT INTO " + self.table_feed + \
              " (etag, title, subtitle, updated)" + \
              " VALUES (?, ?, ?, ?)"
        cur = self.db.cursor()
        cur.execute(sql, [feed.etag, feed.title, feed.subtitle, feed.updated])
        self.db.commit()
        feed.feed_id = cur.lastrowid

    def _update_feed(self, feed):
        if feed.id == "" or feed.id is None:
            raise RuntimeWarning("Can't update because no id found")
        sql = "UPDATE"

    def _create_tables(self):
        sql = 'CREATE TABLE IF NOT EXISTS ' + self.table_feed + \
              ' ( id INTEGER PRIMARY KEY AUTOINCREMENT,  ' \
              'etag VARCHAR, ' \
              'title VARCHAR,  ' \
              'subtitle VARCHAR,  ' \
              'updated DATE);'
        cur = self.db.cursor()
        cur.execute(sql)
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS `etag_idx` ON `" + self.table_feed + "` (`etag` )")
        sql = 'CREATE TABLE IF NOT EXISTS ' + self.table_episodes + \
              ' ( id INTEGER PRIMARY KEY AUTOINCREMENT,  ' \
              'rss_feed_id VARCHAR, ' \
              'rss_episode_id VARCHAR NOT NULL, ' \
              'title VARCHAR, ' \
              'subtitle VARCHAR, ' \
              'description BLOB, ' \
              'duration VARCHAR, link VARCHAR, chapters TEXT ,' \
              'published DATE, ' \
              'youtube_upload_date DATE);'
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
