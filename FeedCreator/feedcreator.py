import sys
import os
import getopt
import shutil
import signal
import logging.config
import argparse

if float(sys.version[:3])<3.0:
    import ConfigParser
else:
    import configparser as ConfigParser
import subprocess
from subprocess import STDOUT
try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')
from pkg_resources import resource_filename
from distutils.dir_util import copy_tree
from os.path import dirname, join, expanduser
import datetime
from colorama import Fore, Back, Style
import time
import youtube_dl
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

    def main(self):
        signal.signal(signal.SIGINT, self._exit_gracefully)
        self.downloadVideos()
        self.createFeed()


    def downloadVideos(self):
        """Downloads the videos from the selected playlist to the specified datadir"""

    def createFeed(self):
        """Creates a new RSS feed containig all files present in the datadir folder"""


    def getArguments(self, argv):
        self._checkPythonVersion();
        parser = argparse.ArgumentParser(prog='tube4droid',  description='Downloads the specififed youtoube list to a local directory and creates and Podcast RSS feed which can be susbscribed to get offline youtube on Android devices',  epilog='And that is how you use me')
        parser.add_argument("-p",  "--playlist",  help="youtoube playlist to mirror",  required=False, dest='playlist')
        parser.add_argument("-d",  "--datadir",  help="where downloaded files get stored",  required=False, dest='datadir')
        parser.add_argument("-s",  "--serverdir",  help="where to put the created RSS feed file",  required=False, dest='serverdir')

        args = parser.parse_args(argv)
        self.__playlist = args.playlist
        self.__datadir = args.datadir
        self.__serverdir = args.serverdir

        self.main()
        sys.exit(0)

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
