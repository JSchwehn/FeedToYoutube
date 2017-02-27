# -*- coding: utf-8 -*-

# import sqlite3
# import feedparser
# import datetime
# import sys
# from feed import Feed
# from episode import Episode
# from chapter import Chapter
# import pprint

import httplib
import httplib2
import os
import random
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
import argparse


class YtUploader:

    config = None
    CLIENT_SECRETS_FILE = "client_secrets.json"
    MISSING_CLIENT_SECRETS_MESSAGE = """
    WARNING: Please configure OAuth 2.0

    To make this sample run you will need to populate the client_secrets.json file
    found at:

       %s

    with information from the {{ Cloud Console }}
    {{ https://cloud.google.com/console }}

    For more information about the client_secrets.json file format, please visit:
    https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
    """ % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))

    # This OAuth 2.0 access scope allows for full read/write access to the
    # authenticated user's account.
    YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    SECTION_TYPES = ("allPlaylists", "completedEvents", "likedPlaylists",
                     "likes", "liveEvents", "multipleChannels", "multiplePlaylists",
                     "popularUploads", "recentActivity", "recentPosts", "recentUploads",
                     "singlePlaylist", "upcomingEvents",)
    SECTION_STYLES = ("horizontalRow", "verticalList",)

    # Explicitly tell the underlying HTTP transport library not to retry, since
    # we are handling retry logic ourselves.
    httplib2.RETRIES = 1

    # Maximum number of times to retry before giving up.
    MAX_RETRIES = 10

    # Always retry when these exceptions are raised.
    RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
                            httplib.IncompleteRead, httplib.ImproperConnectionState,
                            httplib.CannotSendRequest, httplib.CannotSendHeader,
                            httplib.ResponseNotReady, httplib.BadStatusLine)

    # Always retry when an apiclient.errors.HttpError with one of these status
    # codes is raised.
    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

    VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

    args = None

    def __init__(self, config):
        self.config = config


    def get_authenticated_service(self, args):
        flow = flow_from_clientsecrets(self.CLIENT_SECRETS_FILE, scope=self.YOUTUBE_SCOPE,
                                       message=self.MISSING_CLIENT_SECRETS_MESSAGE)

        storage = Storage("%s-oauth2.json" % sys.argv[0])
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, args)

        return build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
                     http=credentials.authorize(httplib2.Http()))

    def initialize_upload(self, youtube, options):
        tags = None
        if options.keywords:
            tags = options.keywords.split(",")

        body = dict(
            snippet=dict(
                title=options.title,
                description=options.description,
                tags=tags,
                categoryId=options.category
            ),
            status=dict(
                privacyStatus=options.privacyStatus
            )
        )

        # Call the API's videos.insert method to create and upload the video.
        insert_request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            # The chunksize parameter specifies the size of each chunk of data, in
            # bytes, that will be uploaded at a time. Set a higher value for
            # reliable connections as fewer chunks lead to faster uploads. Set a lower
            # value for better recovery on less reliable connections.
            #
            # Setting "chunksize" equal to -1 in the code below means that the entire
            # file will be uploaded in a single HTTP request. (If the upload fails,
            # it will still be retried where it left off.) This is usually a best
            # practice, but if you're using Python older than 2.6 or if you're
            # running on App Engine, you should set the chunksize to something like
            # 1024 * 1024 (1 megabyte).
            media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
        )

        self.resumable_upload(insert_request)

    # This method implements an exponential backoff strategy to resume a
    # failed upload.
    def resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                print "Uploading file..."
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print "Video id '%s' was successfully uploaded." % response['id']
                    else:
                        exit("The upload failed with an unexpected response: %s" % response)
            except HttpError, e:
                if e.resp.status in self.RETRIABLE_STATUS_CODES:
                    error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                         e.content)
                else:
                    raise
            except self.RETRIABLE_EXCEPTIONS, e:
                error = "A retriable error occurred: %s" % e

            if error is not None:
                print error
                retry += 1
                if retry > self.MAX_RETRIES:
                    exit("No longer attempting to retry.")

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print "Sleeping %f seconds and then retrying..." % sleep_seconds
                time.sleep(sleep_seconds)

    def upload(self, file_name, episode):
        if hasattr(self.config, 'yt_client_secrets_file'):
            self.CLIENT_SECRETS_FILE = self.config.yt_client_secrets_file

        argparser = argparse.ArgumentParser()
        argparser.add_argument("--file", required=True, help="Video file to upload")
        argparser.add_argument("--title", help="Video title", default="Test Title")
        argparser.add_argument("--description", help="Video description", default="Test Description")
        argparser.add_argument("--category", default="22",
                               help="Numeric video category. " +
                                    "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
        argparser.add_argument("--keywords", help="Video keywords, comma separated",
                               default="")
        argparser.add_argument("--privacyStatus", choices=self.VALID_PRIVACY_STATUSES,
                               default=self.VALID_PRIVACY_STATUSES[1], help="Video privacy status.")
        argparser.add_argument(
            '--logging_level', default='ERROR',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            help='Set the logging level of detail.')
        argparser.add_argument('--auth_host_name', default='localhost',
                            help='Hostname when running a local web server.')
        argparser.add_argument('--noauth_local_webserver', action='store_true',
                            default=False, help='Do not run a local web server.')
        argparser.add_argument('--auth_host_port', default=[8080, 8090], type=int,
                            nargs='*', help='Port web server should listen on.')

        description = episode.description + "\n\n"
        for c in episode.chapters:
            description += c.start + " - " + c.title + "\n"

        self.args = argparser.parse_args(["--file", file_name, "--title", episode.title, "--description", description])
        youtube = self.get_authenticated_service(self.args)
        try:
            self.initialize_upload(youtube, self.args)
        except HttpError, e:
            print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)



