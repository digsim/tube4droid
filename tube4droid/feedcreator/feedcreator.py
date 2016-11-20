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
import time
from colorama import Fore, Back, Style
import mimetypes
import youtube_dl
import json
import glob
import hashlib
import re
from rfeed import *

class Tube4Droid:
    def __init__(self):
        self.__log = logging.getLogger('Tube4Droid')

    def downloadVideos(self):
        """Downloads the videos from the selected playlist to the specified datadir"""
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.__playlist])

    def createFeed(self):
        """Creates a new RSS feed containig all files present in the datadir folder"""
        self.__log.info(self.__datadir)
        rssitems = []
        metafiles = os.path.join(self.__datadir,"*.json")
        metas = glob.glob(metafiles)
        metas.sort(key=os.path.getmtime)
        for meta in metas:
            self.__log.info("Processing item "+meta)
            with open(meta) as json_data:
                itemdata = json.load(json_data)
                json_data.close()
                uploaddate =  itemdata['upload_date']
                filename = os.path.relpath(itemdata['_filename'], self.__datadir)
                description = itemdata['description']
                duration = itemdata['duration']
                fulltitle = itemdata['fulltitle']
                tags = itemdata['tags']
                thumbnail = self.__serveruri+os.path.splitext(os.path.basename(filename))[0]+'.jpg'
                author = itemdata['uploader']
                itunes_item = iTunesItem(
                    author = author,
                    image = thumbnail,
                    duration = duration,
                    explicit = "clean",
                    #subtitle = "The subtitle of the podcast episode",
                    summary = description
                )
                enclosure = Enclosure(
                    url = self.__serveruri+filename,
                    length=duration,
                    type=mimetypes.guess_type(itemdata['_filename'])[0] or 'video/mp4'
                )
                item = Item(
                    title=fulltitle,
                    link=self.__serveruri+filename,
                    description=description,
                    author=author,
                    guid=Guid(hashlib.sha512((self.__serveruri+re.sub('^\d+_', '', filename)).encode('utf-8')).hexdigest()),
                    pubDate=datetime.datetime.strptime(time.ctime(os.path.getmtime(meta)), "%a %b %d %H:%M:%S %Y"),
                    categories=tags,
                    extensions = [itunes_item],
                    enclosure=enclosure
                )
                rssitems.append(item)
        itunes = iTunes(
            author = "Andreas Ruppen",
            subtitle = "Offline Youtube Movies for Podcatcher Software",
            summary = "Liber8Youtube",
            image = "http://www.example.com/artwork.jpg",
            explicit = "clean",
            categories = iTunesCategory(name = 'Technology', subcategory = 'Software How-To'),
            owner = iTunesOwner(name = 'Andreas Ruppen', email = 'andreas.ruppen@gmail.com')
        )

        feed = Feed(
            title="Andys Podcatcher",
            link=self.__serveruri+"rss",
            description = "Offline Youtube Movies for Podcatcher Software",
            language = "en-US",
            lastBuildDate = datetime.datetime.now(),
            items = rssitems,
            extensions = [itunes]
        )
        rssfile = open(os.path.join(self.__serverdir, 'rss'), 'w')
        rssfile.write(feed.rss())




    def _my_hook(self, d):
        if d['status'] == 'finished':
            self.__log.info('Done downloading, now converting ...')

if __name__ == "__main__":
    t4d = Tube4Droid()
    t4d.getArguments(sys.argv[1:])
