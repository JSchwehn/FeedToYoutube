# -*- coding: utf-8 -*-
from multiprocessing import cpu_count
import moviepy.editor as mpe
from moviepy.tools import cvsecs
from hashlib import md5
import requests
import os
import sys
from path import path
import re
#from ytUpload import YtUploader
from imageProcessor import ImageProcessor


class VideoCreator:

    nprocs = 4

    @property
    def image_processor(self):
        return self.image_processor

    @image_processor.setter
    def image_processor(self, value):
        self.image_processor = value

    @image_processor.getter
    def image_processor(self):
        return self.image_processor


    @property
    def thread_count(self):
        return self.thread_count

    @thread_count.setter
    def thread_count(self, value):
        self.thread_count = value

    @property
    def feed(self):
        return self.feed

    @feed.setter
    def feed(self, value):
        self.feed = value

    @property
    def backgroundImage(self):
        return self.backgroundImage

    @backgroundImage.setter
    def backgroundImage(self, value):
        self.backgroundImage = value

    def run(self, feed):
        """

        :param feed:
        :return:
        """
        if not hasattr(feed, 'getNewEpisodes'):
            return None

        self.nprocs = cpu_count()
        self.image_processor = ImageProcessor(self.config)

        new_episodes = feed.getNewEpisodes()
        for episode in new_episodes:
            output = "output/" + self.slugify(episode.title) + ".mp4"

            if not os.path.isfile(output):
                print "Audio Link: " + episode.link
                audio_clip = mpe.AudioFileClip(self.download(episode.link))
                self.image_processor.make_image1(episode)

                self.createMovie(episode=episode, audioClip=audio_clip, output=output)

            #YtUploader(self.config).upload(output, episode)

    def get_chapter_duration(self, chapters, full_duration=None, idx=None):
        """

        :param chapters:
        :param full_duration:
        :param idx:
        :return:
        """
        start = cvsecs(chapters[idx].start)
        if idx is 0:
            start = 0
        try:
            chapter_end_time = chapters[idx + 1].start
        except IndexError:
            chapter_end_time = full_duration

        chapter_end_time = cvsecs(chapter_end_time)
        duration = chapter_end_time - start

        return duration

    def createMovie(self, episode=None, audioClip=None, output=None):
        """

        :param episode:
        :param audioClip:
        :param output:
        :return:
        """
        print " Creating Clips ..."
        if episode is None or audioClip is None:
            return None
        full_duration = audioClip.duration

        if self.config.test:
            full_duration = float(10)

        clips = []

        for idx, chapter in enumerate(episode.chapters):
            clips.append(self.createClip(chapter, self.get_chapter_duration(episode.chapters, idx=idx,
                                                                            full_duration=float(full_duration))))
        if output is None:
            output = "output/" + self.slugify(episode.title) + ".mp4"

        fps = 29.98
        if hasattr(self.config, 'video_fps'):
            fps = self.config.video_fps

        final = mpe.concatenate_videoclips(clips, method="compose")

        if not self.config.test:
            final = final.set_audio(audioClip)

        final.write_videofile(output, threads=self.nprocs, fps=float(fps),
                              temp_audiofile=self.config.temp_path + 'temp-audio.mp3',
                              audio_codec=self.config.audio_codec, codec=self.config.video_codec,
                              bitrate=self.config.video_bitrate)
        self.cleanup()

    def cleanup(self):
        """

        :return:
        """
        d = path(self.config.temp_path)
        for file in d.files('*.png'):
            file.remove()
            print "Removed {} file".format(file)
        for file in d.files('*.mp3'):
            file.remove()
            print "Removed {}".format(file)

    def createClip(self, chapter, duration=10):
        """
        Creates small clips based on the chapter images.

        :param chapter:
        :param duration:
        :return:
        """
        filename = md5(chapter.title.encode('utf-8')).hexdigest()
        img = self.config.temp_path + filename + ".png"
        if not os.path.isfile:
            print "File not found"
            return None
        clip = mpe.ImageClip(img, duration=duration)
        clip.duration = duration
        return clip

    def download(self, link):
        file_name = self.config.temp_path + os.path.basename(link)
        if os.path.isfile(file_name):
            return file_name
        with open(file_name, "wb") as f:
            print "Downloading %s" % file_name
            response = requests.get(link, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
        return file_name

    def slugify(self, value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        """
        import unicodedata
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
        value = unicode(re.sub('[-\s]+', '-', value))
        return value

    def __init__(self, config):
        self.config = config
