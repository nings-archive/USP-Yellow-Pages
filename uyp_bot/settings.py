from os import path
from configparser import ConfigParser

PACKAGE_DIR = path.dirname(path.realpath(__file__))
PROJECT_DIR = path.split(PACKAGE_DIR)[0]

FILENAME_CONFIG = path.join(PROJECT_DIR, 'config.ini')
CONFIG = ConfigParser()
CONFIG.read(FILENAME_CONFIG)
