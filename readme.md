# Podcast RSS Feed to Youtube
 
This is not even in a alpha state. 

##Progress

- [x] subscribe to given podcast feed
- [x] extract data from rss feed
- [x] avoid multiple uploads
- [x] extract image from URL
- [x] create movie
- [ ] upload to youtube
- [ ] detect chapter images and display those
- [ ] prepend intro video
    - [ ] adjust audio
- [ ] append outro video
    - [ ] adjust audio
 
 

##Usage
    usage: feedToYoutube.py [-h] -c MY_CONFIG [-f FEED [FEED ...]]
                            [-vw VIDEO_WIDTH] [-vh VIDEO_HEIGHT] [-fps VIDEO_FPS]
                            [-br VIDEO_RATE] [-codec VIDEO_CODEC] [-db DB_NAME]
                            [-i INIT] [-b BACKGROUND_IMAGE] [-l LAST_EPISODE_ONLY]
                            [-force-upload FORCE_UPLOAD] [-t TEMP_PATH]
                            [-o OUTPUT] [-font FONT]
                            [-font-size-max FONT_SIZE_MAX]
                            [-font-size-min FONT_SIZE_MIN]
                            [-font-color-red FONT_COLOR_RED]
                            [-font-color-green FONT_COLOR_GREEN]
                            [-font-color-blue FONT_COLOR_BLUE]
                            [-title-pos-top TITLE_POS_TOP]
                            [-subtitle-pos-top SUBTITLE_POS_TOP] [-test TEST]
    
    Args that start with '--' (eg. -f) can also be set in a config file
    (./config.yaml or specified via -c).
    
    optional arguments:
      -h, --help            show this help message and exit
      -c MY_CONFIG, --my-config MY_CONFIG
                            Config file path
      -f FEED [FEED ...], --feed FEED [FEED ...]
                            URL to the atom feed
      -vw VIDEO_WIDTH, --video-width VIDEO_WIDTH
                            Video width in pixels
      -vh VIDEO_HEIGHT, --video-height VIDEO_HEIGHT
                            Video height in pixels
      -fps VIDEO_FPS, --video-fps VIDEO_FPS
                            Video frames per seconds
      -br VIDEO_RATE, --video-rate VIDEO_RATE
                            Bitrate for the video
      -codec VIDEO_CODEC, --video-codec VIDEO_CODEC
                            Video Codec
      -db DB_NAME, --db-name DB_NAME
                            Name of the local feed database
      -i INIT, --init INIT  Imports feed with out any video processing and
                            uploading
      -b BACKGROUND_IMAGE, --background-image BACKGROUND_IMAGE
                            Path to a background image
      -l LAST_EPISODE_ONLY, --last-episode-only LAST_EPISODE_ONLY
                            Only process last episode
      -force-upload FORCE_UPLOAD, --force-upload FORCE_UPLOAD
                            Force Upload to youtube
      -t TEMP_PATH, --temp-path TEMP_PATH
                            Where to store temp data
      -o OUTPUT, --output OUTPUT
                            Where to store the created movie
      -font FONT, --font FONT
                            Path to a eot font file
      -font-size-max FONT_SIZE_MAX, --font-size-max FONT_SIZE_MAX
                            Max font size in px
      -font-size-min FONT_SIZE_MIN, --font-size-min FONT_SIZE_MIN
                            Min font size in px
      -font-color-red FONT_COLOR_RED, --font-color-red FONT_COLOR_RED
                            Font color red part 0-255
      -font-color-green FONT_COLOR_GREEN, --font-color-green FONT_COLOR_GREEN
                            Font color green part 0-255
      -font-color-blue FONT_COLOR_BLUE, --font-color-blue FONT_COLOR_BLUE
                            Font color blue part 0-255
      -title-pos-top TITLE_POS_TOP, --title-pos-top TITLE_POS_TOP
                            Top position og the main title
      -subtitle-pos-top SUBTITLE_POS_TOP, --subtitle-pos-top SUBTITLE_POS_TOP
                            Top position og the main subtitle
      -test TEST, --test TEST
                            Do not render the whole movie, just 10 sec
    
