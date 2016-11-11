# -*- coding: utf-8 -*-

from episode import Episode
from PIL import Image, ImageFont, ImageDraw
from hashlib import md5


class VideoCreator:
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
            print "\t creating image " + episode.title
            self.make_image1(episode)

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
            img = Image.open(self.config.background_image)
            draw = ImageDraw.Draw(img)

            self.draw_title(episode, draw, img)
            self.draw_chapter(episode.chapters[0], draw, img)
            img.save('tmp/' + md5(episode.title.encode('utf-8')).hexdigest() + '.png')
        pass

    def draw_title(self, episode, draw, img):
        if hasattr(self.config, "font"):
            img_fraction_title = 0.8
            font_size = 18  # todo min font size -> config
            title_font = self.get_dynamic_font_size(episode.title, img, canvas_fraction=img_fraction_title)
            font_x_pos, font_y_pos = title_font.getsize(episode.title)
            title_pos_left = (img.size[0] / 2) - font_x_pos / 2
            title_pos_top = (img.size[1] / 2) - font_size / 2
            title_pos_top -= 48  # offset todo ->config
            draw.text((title_pos_left, title_pos_top), episode.title, (128, 128, 128), font=title_font)

    def draw_dynamic_centered_text(self):
        pass

    def draw_chapter(self, chapter, draw, img):
        if hasattr(self.config, "font"):
            text = chapter.title
            img_fraction = 0.4  # todo -> config
            font_size = 18  # todo -> config
            title_font = self.get_dynamic_font_size(text, img, canvas_fraction=img_fraction)
            font_x_pos, font_y_pos = title_font.getsize(text)
            title_pos_left = (img.size[0] / 2) - font_x_pos / 2
            title_pos_top = (img.size[1] / 2) - font_size / 2
            title_pos_top -= -200  # todo -> config
            draw.text((title_pos_left, title_pos_top), text, (128, 128, 128), font=title_font)

    def __init__(self, config):
        self.config = config
