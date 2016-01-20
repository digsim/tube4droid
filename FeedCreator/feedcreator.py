from __future__ import unicode_literals
import sys
import os
import shutil
import signal
import logging.config
import argparse

if float(sys.version[:3])<3.0:
    import ConfigParser
else:
    import configparser as ConfigParser
try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')
from os.path import dirname, join, expanduser
import datetime
from colorama import Fore, Back, Style
import youtube_dl
import json
import glob
from rfeed import *

class Tube4Droid:
    def __init__(self):
        self.original_sigint = signal.getsignal(signal.SIGINT)
        self.__CONFIG_DIR = '/etc/Tube4Droid/'
        self.__USER_CONFIG_DIR = expanduser('~/.Tube4Droid')
        self._checkUserConfigFiles()

        logging.basicConfig(level=logging.ERROR)
        logging.config.fileConfig(
            [join(self.__USER_CONFIG_DIR, 'logging.conf'), expanduser('~/.logging.conf'), 'logging.conf'],
            defaults={'logfilename': os.path.join(expanduser('~/.Tube4Droid'), 'tube4droid.log')})
        self.__log = logging.getLogger('Tube4Droid')

        # Configure several elements depending on config file
        if float(sys.version[:3])<3.2:
            config = ConfigParser.SafeConfigParser()
        else:
            config = ConfigParser.ConfigParser()
        config.read([join(self.__USER_CONFIG_DIR, 'tube4droid.conf'), expanduser('~/.tube4droid.conf'), 'tube4droid.conf'])
        self.__cwd = os.getcwd()
        self.__playlist = config.get('Config', 'playlist')
        self.__datadir = config.get('Config', 'mediadir')
        self.__serverdir = config.get('Config', 'rssdir')
        self.__serveruri = config.get('Config', 'serveruri')

        self.ydl_opts = {
            #'format': 'bestaudio/best',
            #'postprocessors': [{
            #    'key': 'FFmpegExtractAudio',
            #    'preferredcodec': 'mp3',
            #    'preferredquality': '192',
            #}],
            'username': '***REMOVED***',
            'password': '***REMOVED***',
            'simulate': 'true',
            'outtmpl': os.path.join(self.__datadir,'%(title)s.%(ext)s'),
            'restrictfilenames': 'true',
            'playliststart': 1,
            'writeinfojson': 'true',
            'writethumbnail': 'true',
            'call_home': 'true',
            'logger': self.__log,
            'progress_hooks': [self._my_hook],
        }

    def main(self):
        signal.signal(signal.SIGINT, self._exit_gracefully)
        self.downloadVideos()
        self.createFeed()


    def downloadVideos(self):
        """Downloads the videos from the selected playlist to the specified datadir"""
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download(['https://www.youtube.com/playlist?list=PLUeWws_6XlvfxEcYrDIVyqTsaWc4g7UGT'])

    def createFeed(self):
        """Creates a new RSS feed containig all files present in the datadir folder"""
        self.__log.info(self.__datadir)
        rssitems = []
        metafiles = os.path.join(self.__datadir,"*.json")
        for meta in glob.glob(metafiles):
            with open(meta) as json_data:
                itemdata = json.load(json_data)
                json_data.close()
                #self.__log.debug(itemdata)
                uploaddate =  itemdata['upload_date']
                filename = os.path.relpath(itemdata['_filename'], self.__datadir)
                description = itemdata['description']
                duration = itemdata['duration']
                fulltitle = itemdata['fulltitle']
                tags = itemdata['tags']
                thumbnail = itemdata['thumbnail']
                author = itemdata['uploader']
                item = Item(
                    title=fulltitle,
                    link=self.__serveruri+filename,
                    description=description,
                    author=author,
                    guid=Guid(self.__serveruri+filename),
                    pubDate=datetime.datetime(int(uploaddate[0:4]), int(uploaddate[4:6]), int(uploaddate[6:8]), 10, 00),
                    categories=tags
                )
                rssitems.append(item)
        feed = Feed(
            title="Andys Podcatcher",
            link=self.__serveruri+"rss",
            description = "Offline Youtube Movies for Podcatcher Software",
            language = "en-US",
            lastBuildDate = datetime.datetime.now(),
            items = rssitems
        )
        rssfile = open(os.path.join(self.__serverdir, 'rss'), 'w')
        rssfile.write(feed.rss())



    def getArguments(self, argv):
        self._checkPythonVersion();
        parser = argparse.ArgumentParser(prog='tube4droid',  description='Downloads the specififed youtoube list to a local directory and creates and Podcast RSS feed which can be susbscribed to get offline youtube on Android devices',  epilog='And that is how you use me')
        parser.add_argument("-p",  "--playlist",  help="youtoube playlist to mirror",  required=False, dest='playlist')
        parser.add_argument("-d",  "--datadir",  help="where downloaded files get stored",  required=False, dest='datadir')
        parser.add_argument("-s",  "--serverdir",  help="where to put the created RSS feed file",  required=False, dest='serverdir')

        args = parser.parse_args(argv)
        self.__playlist = args.playlist or self.__playlist
        self.__datadir = args.datadir or self.__datadir
        self.__serverdir = args.serverdir or self.__serverdir

        self.main()
        sys.exit(0)

    def _my_hook(self, d):
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')
        else:
            print('ongoing')

    def _checkPythonVersion(self):
        if float(sys.version[:3])<3.0:
            self.__log.debug("Using Python 2")
        else:
            self.__log.debug("Using Python 3")

    def _checkUserConfigFiles(self):
        if not os.path.exists(self.__CONFIG_DIR):
            return
        if not os.path.exists(self.__USER_CONFIG_DIR):
            os.mkdir(self.__USER_CONFIG_DIR)
        if not os.path.exists(join(self.__USER_CONFIG_DIR, 'logging.conf')):
            shutil.copy(join(self.__CONFIG_DIR, 'logging.conf'), join(self.__USER_CONFIG_DIR, 'logging.conf'))
        if not os.path.exists(join(self.__USER_CONFIG_DIR, 'tube4droid.conf')):
            shutil.copy(join(self.__CONFIG_DIR, 'tube4droid.conf'), join(self.__USER_CONFIG_DIR, 'tube4droid.conf'))


    def _exit_gracefully(self, signum, frame):
        # restore the original signal handler as otherwise evil things will happen
        # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
        signal.signal(signal.SIGINT, self.original_sigint)
        if float(sys.version[:3])<3.0:
            real_raw_input=raw_input
        else:
            real_raw_input=input

        try:
            if real_raw_input('\nReally quit? (y/n)> ').lower().startswith('y'):
                sys.exit(1)
        except KeyboardInterrupt:
            print("Ok ok, quitting")
            sys.exit(1)

        # restore the exit gracefully handler here
        signal.signal(signal.SIGINT, self._exit_gracefully)


if __name__ == "__main__":
    t4d = Tube4Droid()
    t4d.getArguments(sys.argv[1:])
