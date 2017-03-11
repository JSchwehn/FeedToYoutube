# -*- coding: utf-8 -*-

from PIL import Image, ImageFont, ImageDraw
from multiprocessing import Process, Queue, current_process, cpu_count
from hashlib import md5


class ImageProcessor:

    config = None
    nprocs = 4

    def __init__(self, config):
        """

        :param config:
        """
        self.config = config
        self.nprocs = cpu_count()

    def image_worker(self, episode_text, work_queue, done_queue):
        """

        :param episode_text:
        :param work_queue:
        :param done_queue:
        :return:
        """
        try:
            for chapter in iter(work_queue.get, 'STOP'):
                filename = self.config.temp_path + md5(chapter.title.encode('utf-8')).hexdigest() + '.png'
                img = Image.open(self.config.background_image)
                size = (int(self.config.video_width), int(self.config.video_height))

                # handle small background images
                if img.size[0] <> int(self.config.video_width) or img.size[1] <> int(self.config.video_height):
                    img.thumbnail(size, Image.ANTIALIAS)  # generating the thumbnail from given size

                    offset_x = max((size[0] - img.size[0]) / 2, 0)
                    offset_y = max((size[1] - img.size[1]) / 2, 0)
                    offset_tuple = (offset_x, offset_y)  # pack x and y into a tuple

                    final_thumb = Image.new(mode='RGB', size=size,
                                            color=self.hex_to_rgb(self.config.video_background_color))
                    final_thumb.paste(img, offset_tuple)
                    img = final_thumb

                self.draw_title(episode_text, img)
                self.draw_chapter(chapter.title, img)
                img.save(filename)
                done_queue.put("%s - %s got %s." % (current_process().name, filename, filename))
        except Exception, e:
            filename = self.config.temp_path + md5(chapter.title.encode('utf-8')).hexdigest() + '.png'
            done_queue.put("%s failed on %s with: %s" % (current_process().name, filename, e.message))
        return True

    def make_image1(self, episode=None):
        """

        :param episode:
        :return:
        """
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
        """

        :param episode_title:
        :param img:
        :return:
        """
        if hasattr(self.config, "font"):
            img_fraction_title = 0.8
            font_size = int(self.config.font_size_min)
            text_pos_top = (img.size[1] / 2) - font_size / 2
            text_pos_top += int(self.config.title_pos_top)
            self.draw_dynamic_centered_text(episode_title, img, self.hex_to_rgb(self.config.font_color), img_fraction_title, font_size,
                                            text_pos_top=text_pos_top)

    def draw_chapter(self, chapter_title, img):
        """

        :param chapter_title:
        :param img:
        :return:
        """
        if hasattr(self.config, "font"):
            img_fraction = 0.6  # todo -> config
            font_size = int(self.config.font_size_min)  # todo -> config
            text_pos_top = (img.size[1] / 2) - font_size / 2
            text_pos_top += int(self.config.subtitle_pos_top)
            self.draw_dynamic_centered_text(chapter_title, img, self.hex_to_rgb(self.config.font_color_subtitle), img_fraction, font_size, text_pos_top=text_pos_top)

    def get_dynamic_font_size(self, text, img, canvas_fraction=0.9):
        font_size = int(self.config.font_size_min)
        font = ImageFont.truetype(self.config.font, font_size)
        while font.getsize(text)[0] < canvas_fraction * img.size[0]:
            if font_size > int(self.config.font_size_max):
                break
            font_size += 1
            font = ImageFont.truetype(self.config.font, font_size)
        return font

    def draw_dynamic_centered_text(self, text, img, font_color=(255,255,255), img_fraction=0.9, min_font_size=18, text_pos_top=0):
        """

        :param font_color: (int,int,int)
        :param text:
        :param img:
        :param img_fraction:
        :param min_font_size:
        :param text_pos_top:
        :return:
        """
        if hasattr(self.config, "font"):
            draw = ImageDraw.Draw(img)
            dynamic_font = self.get_dynamic_font_size(text, img, canvas_fraction=img_fraction)
            font_x_pos, font_y_pos = dynamic_font.getsize(text)
            text_pos_left = (img.size[0] / 2) - font_x_pos / 2
            draw.text((text_pos_left, text_pos_top), text, font_color, font=dynamic_font)

    def hex_to_rgb(self, value):
        """Return (red, green, blue) for the color given as #rrggbb."""
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
