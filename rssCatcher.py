# -*- coding: utf-8 -*-
import sqlite3
import feedparser
import datetime
import sys
from feed import Feed
from episode import Episode
from chapter import Chapter
import pprint


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
        feedparser.USER_AGENT = "FeedToYoutube/0.0.3 +http://ldk.net/"
        f = feedparser.parse(self.feed_url, request_headers={'content-type': 'text/html; charset=UTF-8'})
        if not hasattr(f, "etag"):
            if hasattr(f.feed, "updated"):
                etag = f.feed.updated
            else:
                raise LookupError('Can\'t find any update indicator. please contact the author.')
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

        feed = Feed(self.config, feedUrl,
                    image=imageUrl,
                    etag=etag,
                    subtitle=f.feed.summary,
                    title=f.feed.title,
                    updated=f.feed.updated
                    )

        self.save_feed(feed)
        feed.episodes = []

        print "Importing " + feed.title
        for episode in f.entries:
            sys.stdout.write(" Episode " + episode.title)
            sys.stdout.flush()
            if self._is_known_episode(episode.id):
                print " - old"
                feed.episodes.append(self.load_episode_by_rss_id(rss_episode_id=episode.id))
                continue

            print " - new"
            is_new = True
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
            duration = ""
            if hasattr(episode, 'image') and hasattr(episode.image, "href"):
                image = episode.image.href
            if hasattr(episode, 'itunes_duration'):
                duration = episode.itunes_duration
            if hasattr(episode, "links"):
                for link in episode.links:
                    if link.type == 'audio/mpeg':
                        link = link.href
                        break

            e = Episode(feed_id=feed.feed_id,
                        rss_episode_id=episode.id,
                        duration=duration,
                        link=link,
                        title=episode.title,
                        subtitle=episode.subtitle,
                        description=episode.summary,
                        published=episode.published,
                        chapters=cs,
                        image=image,
                        is_new=is_new
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
        sql = "INSERT OR IGNORE INTO " + self.table_feed + \
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
              'movie_created DATE, ' \
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

    def load_episode_by_rss_id(self, rss_episode_id=None):
        sql = "SELECT * FROM " + self.table_episodes + " AS e  WHERE rss_episode_id = ? LIMIT 1"
        cur = self.db.cursor()

        cur.row_factory = sqlite3.Row
        cur.execute(sql, [rss_episode_id])
        d = cur.fetchone()
        e = Episode(episode_id=d['id'],
                    rss_episode_id=d["rss_episode_id"],
                    duration=d["duration"],
                    title=d["title"],
                    description=d["description"],
                    subtitle=d["subtitle"],
                    link=d["link"],
                    published=d["published"],
                    image=d["image"],
                    chapters=[]
                    )
        sql = "SELECT * FROM " + self.table_chapters + " WHERE episode_id = ?"
        cur.row_factory = sqlite3.Row
        cur.execute(sql, [d["id"]])
        d = cur.fetchall()
        chapters = []
        for c in d:
            chapters.append(
                Chapter(c["start"], c["title"], chapter_id=c["id"], episode_id=c["episode_id"], image=c["image"],
                        href=c["href"]))
        e.chapters = chapters
        return e

    def _feed_has_changed(self, etag):
        if self.config.force_upload == 'True':
            return True
        cur = self.db.cursor()
        cur.execute("SELECT etag FROM " + self.table_feed + " WHERE etag = ?", [etag])
        data = cur.fetchall()
        if len(data) > 0:
            return False
        else:
            return True

    def _is_known_episode(self, episode_id):
        cur = self.db.cursor()
        cur.execute("SELECT rss_episode_id FROM " + self.table_episodes + " WHERE rss_episode_id = ?", [episode_id])
        data = cur.fetchall()
        if len(data) > 0:
            return True
        else:
            return False

    def mark_movie_created(self):
        pass

    def mark_movie_uploaded(self):
        pass
