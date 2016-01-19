import sys
from .feedcreator import Tube4Droid


def main():
    """Entry point for the application script"""
    t4d = Tube4Droid()
    t4d.getArguments(sys.argv[1:])