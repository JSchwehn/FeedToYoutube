import configargparse
from rssCatcher import RssCatcher
from videoCreator import VideoCreator

class RssVideoCreator:
    config = None
    db = None
    table_feed = ""
    table_episodes = ""
    rss_catcher = None
    feeds = []
    argparser = None

    def __init__(self):
        self.load_config()

    def load_config(self):
        p = configargparse.ArgParser(default_config_files=['./config.yaml'])
        p.add('-c', '--my-config', required=True, is_config_file=True, help='Config file path')
        p.add('-f', '--feed', nargs="+", help='URL to the atom feed')
        p.add('-vw', '--video-width', help='Video width in pixels')
        p.add('-vh', '--video-height', help='Video height in pixels')
        p.add('-fps', '--video-fps', help='Video frames per seconds')
        p.add('-br', '--video-bitrate', help='Bitrate for the video')
        p.add('-vbc', '--video-background-color', help='HTML Hex Color String e.g. #fefefe')
        p.add('-codec', '--video-codec', help='Video Codec')
        p.add('-audio-codec', '--audio-codec', help='Audio Codec')
        p.add('-db', '--db-name', help='Name of the local feed database')
        p.add('-i', '--init', help='Imports feed with out any video processing and uploading')
        p.add('-b', '--background-image', help='Path to a background image')
        p.add('-l', '--last-episode-only', help='Only process last episode')
        p.add('-force-upload', '--force-upload', help='Force Upload to youtube')
        p.add('-t', '--temp-path', help='Where to store temp data')
        p.add('-o', '--output', help='Where to store the created movie')
        p.add('-font', '--font', help='Path to a eot font file')
        p.add('-font-size-max', '--font-size-max', help='Max font size in px')
        p.add('-font-size-min', '--font-size-min', help='Min font size in px')
        p.add('-font-color', '--font-color', help='HTML Color code e.g. #fefefe')
        p.add('-font-color-subtitle', '--font-color-subtitle', help='HTML Hex Color String e.g. #fefefe')
        p.add('-title-pos-top', '--title-pos-top', help='Top position og the main title')
        p.add('-subtitle-pos-top', '--subtitle-pos-top', help='Top position og the main subtitle')
        p.add('-test', '--test', action='store_true', help='Do not render the whole movie, just 10 sec')
        p.add('-secret', '--yt_client_secrets_file', help='Youtube Secret JSON file')
        p.add('-preview', '--preview', help='Render a single frame.')


        self.argparser = p
        self.config = p.parse_args()

    def run(self):
        for feedUrl in self.config.feed:
            VideoCreator(self.config).run(
                RssCatcher(self.config).load_rss(feedUrl)
            )
