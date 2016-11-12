# -*- coding: utf-8 -*-

import moviepy.editor as mpe
import moviepy.config as cf


def main():
    #    cf.change_settings({"FFMPEG_BINARY": r'C:\Program Files\ImageMagick-7.0.3-Q16-HDRI\ffmpeg.exe'})
    audioClip = mpe.AudioFileClip('re009.mp3')
    print "duration", audioClip.duration


if __name__ == '__main__':
    main()
