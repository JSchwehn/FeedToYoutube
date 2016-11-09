import configargparse
from rssCatcher import RssCatcher


class RssVideoCreator:
    config = None
    db = None
    table_feed = ""
    table_episodes = ""
    rss_catcher = None
    feeds = []

    def __init__(self):
        self.load_config()

    def load_config(self):
        p = configargparse.ArgParser(default_config_files=['./config.yaml'])
        p.add('-c', '--my-config', required=True, is_config_file=True, help='Config file path')
        p.add('-f', '--feed', nargs="+", help='URL to the atom feed')
        p.add('-vw', '--video-width', help='Video width in pixels')
        p.add('-vh', '--video-height', help='Video height in pixels')
        p.add('-vfps', '--video-fps', help='Video frames per seconds')
        p.add('-db', '--db-name', help='Name of the local feed database')
        p.add('-i', '--init', help='Imports feed with out any video processing and uploading')
        self.config = p.parse_args()

    def run(self):
        for feedUrl in self.config.feed:
            rssCatcher = RssCatcher(self.config)
            self.feeds.append(rssCatcher.load_rss(feedUrl))
