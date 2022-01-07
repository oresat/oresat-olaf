from .node import OreSatNode
from .common.app import App
from .common.ecss import scet_int_from_time, scet_int_to_time, utc_int_from_time, utc_int_to_time
from .common.oresat_file import OreSatFile, new_oresat_file
from .common.oresat_file_cache import OreSatFileCache

MAJOR = 0
MINOR = 1
PATCH = 0

APP_NAME = 'oresat-linux-node'
APP_DESCRIPTION = 'Framework for all OreSat Linux nodes'
APP_VERSION = '{}.{}.{}'.format(MAJOR, MINOR, PATCH)
APP_AUTHOR = 'PSAS'
APP_EMAIL = 'oresat@pdx.edu'
APP_URL = 'https://github.com/oresat/oresat-linux-node'
APP_LICENSE = 'GPL-3.0'
