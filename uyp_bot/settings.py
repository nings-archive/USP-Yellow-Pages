from os import path
from configparser import ConfigParser

PACKAGE_DIR = path.dirname(path.realpath(__file__))
PROJECT_DIR = path.split(PACKAGE_DIR)[0]
VOLUME_DIR = path.join(PROJECT_DIR, 'volume')

FILENAME_CONFIG = path.join(PROJECT_DIR, 'volume/config.ini')
FILENAME_DB = path.join(VOLUME_DIR, 'uyp.db')

CONFIG = ConfigParser()
CONFIG.read(FILENAME_CONFIG)
