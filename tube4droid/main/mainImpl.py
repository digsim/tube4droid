from .main import Main
import argparse
import sys
import logging
import os
from tube4droid.feedcreator.feedcreator import Tube4Droid


class MainImpl(Main):

    def __init__(self):
        """Constructor"""
        self.__configDirName = "Tube4Droid"
        self.__configName = 'tube4droid.conf'
        self.__logFileName = 'tube4droid.log'

        super(MainImpl, self).__init__(self.__configDirName, self.__configName, self.__logFileName)
        self.__log = logging.getLogger('Tube4Droid')

        self.__cwd = os.getcwd()
        self.__playlist = self.config.get('Config', 'playlist')
        self.__datadir = self.config.get('Config', 'mediadir')
        self.__serverdir = self.config.get('Config', 'rssdir')
        self.__serveruri = self.config.get('Config', 'serveruri')
        self.__ytusername = self.config.has_option('Youtube', 'username') and self.config.get('Youtube', 'username') or None
        self.__ytpassword = self.config.has_option('Youtube', 'password') and self.config.get('Youtube', 'password') or None
        self.__ydl_password_opt = ''

    def getArguments(self, argv):
        """
        Parses the command line arguments.

        :param argv: array of command line arguments
        :return: void
        """
        self._checkPythonVersion()
        parser = argparse.ArgumentParser(prog='tube4droid',
                                         description='Downloads the specififed youtoube list to a local directory and creates and Podcast RSS feed which can be susbscribed to get offline youtube on Android devices',
                                         epilog='%(prog)s {command} -h for help on individual commands')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + self.version)
        subparsers = parser.add_subparsers(help='commands', dest='command')
        sync_parser = subparsers.add_parser('sync', help='sync videos to local directory')
        sync_parser.add_argument("-p", "--playlist", help="youtoube playlist to mirror", required=False, dest='playlist')
        sync_parser.add_argument("-d", "--datadir", help="where downloaded files get stored", required=False, dest='datadir')
        sync_parser.add_argument("-s", "--serverdir", help="where to put the created RSS feed file", required=False,
                            dest='serverdir')

        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)

        args = parser.parse_args(argv)
        self.__playlist = args.playlist or self.__playlist
        self.__datadir = args.datadir or self.__datadir
        self.__serverdir = args.serverdir or self.__serverdir
        self.__command = args.command or None



        if self.__command == 'sync':
            self.main()
        else:
            parser.print_help()
            sys.exit(1)
        sys.exit(0)

    def doWork(self):
        """Overwrites the main"""
        t4d = Tube4Droid(self.__ytusername, self.__ytpassword, self.__datadir, self.__playlist, self.__serverdir, self.__serveruri)
        t4d.downloadVideos()
        t4d.createFeed()


if __name__ == "__main__":
    main = MainImpl()
    main.getArguments(sys.argv[1:])
