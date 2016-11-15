# Podcast RSS Feed to Youtube
 
This is not even in a alpha state. 

##Progress

- [x] subscribe to given podcast feed
- [x] extract data from rss feed
- [x] avoid multiple uploads
- [x] extract image from URL
- [x] create movie
- [ ] prepend intro video
    - [ ] adjust audio
- [ ] append outro video
    - [ ] adjust audio
- [ ] detect chapter images and display those
- [ ] upload to youtube 
 

##Usage
    feedToYoutube.py [-h] -c MY_CONFIG [-f FEED] [-vw VIDEO_WIDTH]
                     [-vh VIDEO_HEIGHT] [-vfps VIDEO_FPS] [-db DB_NAME] [-i INIT]
    
    Args that start with '--' (eg. -f) can also be set in a config file
    (./config.yaml or specified via -c). Config file syntax allows: key=value,
    flag=true, stuff=[a,b,c] (for details, see syntax at https://pypi.python.org/pypi/ConfigArgParse).
    If an arg is specified in more than one place, then commandline values
    override config file values which override defaults.
    
    optional arguments:
      -h, --help            show this help message and exit
      -c MY_CONFIG, --my-config MY_CONFIG
                            config file path
      -f FEED, --feed FEED  URL to the atom feed
      -vw VIDEO_WIDTH, --video-width VIDEO_WIDTH
                            Video width in pixels
      -vh VIDEO_HEIGHT, --video-height VIDEO_HEIGHT
                            Video height in pixels
      -vfps VIDEO_FPS, --video-fps VIDEO_FPS
                            Video frames per seconds
      -db DB_NAME, --db-name DB_NAME
                            Name of the local feed database
      -i INIT, --init INIT  Imports feed with out any video processing and
                            uploading
