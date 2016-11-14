# -*- coding: utf-8 -*-

from episode import Episode
from PIL import Image, ImageFont, ImageDraw
from hashlib import md5
import moviepy.editor as mpe

import requests
import os
import sys
import multiprocessing
import re
import pprint as p

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

        newEpisodes = feed.getNewEpisodes()
        for episode in newEpisodes:
            audioClip = mpe.AudioFileClip(self.download(episode.link))
            print "\t creating images for " + episode.title
            self.make_image1(episode)
            self.createMovie(episode)

    def getChapterDuration(self, chapter):
        # todo implement
        return 3
        pass

    def createMovie(self, episode=None, audioClip=None):
        print " Creating Clips ..."
        if episode is None:
            return None
        clips = []
        for chapter in episode.chapters:
            clips.append(self.createClip(chapter, self.getChapterDuration(chapter)))
        final = mpe.concatenate_videoclips(clips,method="compose")
        output = "output/" + self.slugify(episode.title) + ".mp4"
        fps = 29.98
        if hasattr(self.config, 'video_fps'):
            fps = self.config.video_fps
        
        final.write_videofile(output, fps=float(fps),codec='libx264', bitrate="800k")
        pass

    def createClip(self, chapter, duration=10):
        filename  = md5(chapter.title.encode('utf-8')).hexdigest()
        img = 'tmp/' + filename +".png"
        if not os.path.isfile:
            print "File not found"
            return None
        clip = mpe.ImageClip(img, duration=duration)
        clip.duration = duration
        output = "./"
        if hasattr(self.config, 'output'):
            output = self.config.output
        fps = 29.98
        if hasattr(self.config, 'video_fps'):
            fps = self.config.video_fps
        #output = 'tmp/' + filename + ".mp4"
        #clip.write_videofile(output, fps=float(fps),codec='libx264', bitrate="800k",preset="ultrafast")
        return clip
        pass

    def download(self, link):
        # todo check if the file aready exists
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
        font_size = 18  # todo min font size -> config
        font = ImageFont.truetype(self.config.font, font_size)
        while font.getsize(text)[0] < canvas_fraction * img.size[0]:
            if font_size > 90:  # todo max font size ->config
                break
            font_size += 1
            font = ImageFont.truetype(self.config.font, font_size)
        return font


    def make_image1(self, episode=None):
        # load background image
        if hasattr(self.config, "background_image"):
            cnt = 0
            jobs = []
            for c in episode.chapters:
                p = multiprocessing.Process(target=self.create_image, args=(c.title,episode.title, cnt))
                jobs.append(p)
                cnt += 1
                p.start()
                p.join()

    def create_image(self, chapter_text, episode_text="",  cnt=0):
        print " Start job "+str(cnt)
        img = Image.open(self.config.background_image)
        self.draw_title(episode_text, img)
        self.draw_chapter(chapter_text, img)
        img.save('tmp/' + md5(chapter_text.encode('utf-8')).hexdigest() + '.png')
        print " Finished job "+str(cnt) 


    def draw_title(self, episode_title, img):
        if hasattr(self.config, "font"):
            img_fraction_title = 0.8
            font_size = 18  # todo min font size -> config
            text_pos_top = (img.size[1] / 2) - font_size / 2
            text_pos_top -= 100  # todo -> config
            self.draw_dynamic_centered_text(episode_title, img, img_fraction_title, font_size,
                                            text_pos_top=text_pos_top)

    def draw_chapter(self, chapter_title, img):
        if hasattr(self.config, "font"):
            img_fraction = 0.6  # todo -> config
            font_size = 18  # todo -> config
            text_pos_top = (img.size[1] / 2) - font_size / 2
            text_pos_top -= -200  # todo -> config
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


