# -*- coding: utf-8 -*-

from PIL import Image, ImageFont, ImageDraw
from hashlib import md5
import moviepy.editor as mpe
from moviepy.tools import cvsecs

import requests
import os
import sys
from path import path
from multiprocessing import Process, Queue, current_process, cpu_count
import re
from ytUpload import YtUploader


class VideoCreator:
    nprocs = 4

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
        if not hasattr(feed, 'getNewEpisodes'):
            return None

        self.nprocs = cpu_count()

        new_episodes = feed.getNewEpisodes()
        for episode in new_episodes:
            output = "output/" + self.slugify(episode.title) + ".mp4"

            if not os.path.isfile(output):
                print "Audio Link: " + episode.link
                audio_clip = mpe.AudioFileClip(self.download(episode.link))
                self.make_image1(episode)
                self.createMovie(episode=episode, audioClip=audio_clip, output=output)

            YtUploader(self.config).upload(output, episode)

    def get_chapter_duration(self, chapters, full_duration=None, idx=None):
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
        d = path(self.config.temp_path)
        for file in d.files('*.png'):
            file.remove()
            print "Removed {} file".format(file)
        for file in d.files('*.mp3'):
            file.remove()
            print "Removed {}".format(file)

    def createClip(self, chapter, duration=10):
        filename = md5(chapter.title.encode('utf-8')).hexdigest()
        img = 'tmp/' + filename + ".png"
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

    def get_dynamic_font_size(self, text, img, canvas_fraction=0.9):
        font_size = int(self.config.font_size_min)
        font = ImageFont.truetype(self.config.font, font_size)
        while font.getsize(text)[0] < canvas_fraction * img.size[0]:
            if font_size > int(self.config.font_size_max):
                break
            font_size += 1
            font = ImageFont.truetype(self.config.font, font_size)
        return font

    def image_worker(self, episode_text, work_queue, done_queue):
        try:
            for chapter in iter(work_queue.get, 'STOP'):
                filename = self.config.temp_path + md5(chapter.title.encode('utf-8')).hexdigest() + '.png'
                img = Image.open(self.config.background_image)
                self.draw_title(episode_text, img)
                self.draw_chapter(chapter.title, img)
                img.save(filename)
                done_queue.put("%s - %s got %s." % (current_process().name, filename, filename))
        except Exception, e:
            filename = 'tmp/' + md5(chapter.title.encode('utf-8')).hexdigest() + '.png'
            done_queue.put("%s failed on %s with: %s" % (current_process().name, filename, e.message))
        return True

    def make_image1(self, episode=None):
        print "\t creating images for " + episode.title
        # load background image
        if hasattr(self.config, "background_image"):
            jobs = []
            workers = self.nprocs
            work_queue = Queue()
            done_queue = Queue()
            for c in episode.chapters:
                work_queue.put(c)

            for w in xrange(workers):
                p = Process(target=self.image_worker, args=(episode.title, work_queue, done_queue))
                p.start()
                jobs.append(p)
                work_queue.put('STOP')

            for p in jobs:
                p.join()

            done_queue.put('STOP')
            for status in iter(done_queue.get, 'STOP'):
                print status

    def draw_title(self, episode_title, img):
        if hasattr(self.config, "font"):
            img_fraction_title = 0.8
            font_size = int(self.config.font_size_min)
            text_pos_top = (img.size[1] / 2) - font_size / 2
            text_pos_top += int(self.config.title_pos_top)
            self.draw_dynamic_centered_text(episode_title, img, img_fraction_title, font_size,
                                            text_pos_top=text_pos_top)

    def draw_chapter(self, chapter_title, img):
        if hasattr(self.config, "font"):
            img_fraction = 0.6  # todo -> config
            font_size = int(self.config.font_size_min)  # todo -> config
            text_pos_top = (img.size[1] / 2) - font_size / 2
            text_pos_top += int(self.config.subtitle_pos_top)
            self.draw_dynamic_centered_text(chapter_title, img, img_fraction, font_size, text_pos_top=text_pos_top)

    def draw_dynamic_centered_text(self, text, img, img_fraction=0.9, min_font_size=18, text_pos_top=0):
        if hasattr(self.config, "font"):
            draw = ImageDraw.Draw(img)
            dynamic_font = self.get_dynamic_font_size(text, img, canvas_fraction=img_fraction)
            font_x_pos, font_y_pos = dynamic_font.getsize(text)
            text_pos_left = (img.size[0] / 2) - font_x_pos / 2
            draw.text((text_pos_left, text_pos_top), text, (128, 128, 128), font=dynamic_font)

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
