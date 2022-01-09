import sys
from logging.handlers import SysLogHandler
from argparse import ArgumentParser

from loguru import logger

# public api here
from .node import OreSatNode
from .common.app import App
from .common.ecss import scet_int_from_time, scet_int_to_time, utc_int_from_time, utc_int_to_time
from .common.oresat_file import OreSatFile, new_oresat_file
from .common.oresat_file_cache import OreSatFileCache
from .common.pru import PRU, PRUError, PRUState

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

LOG_FORMAT = '<green>{time}</green> | {level} | <level>{message}</level>'
'''Logger message format'''

logger.remove()  # remove default logger
logger.add(sys.stderr, format=LOG_FORMAT, level='INFO')

node_args_parser = ArgumentParser(add_help=False)
'''The optional, but recommend **parent** :py:class:`ArgumentParser` object to use.'''

node_args_parser.add_argument('-b', '--bus', default='vcan0',
                              help='set the node ID, defaults to vcan0')
node_args_parser.add_argument('-n', '--node-id', type=str, default='0', metavar='ID',
                              help='CAN bus to use')
node_args_parser.add_argument('-v', '--verbose', action='store_true', help='verbose logging')
node_args_parser.add_argument('-l', '--log', action='store_true', help='log to only journald')
node_args_parser.add_argument('-e', '--eds', metavar='FILE', help='EDS/DCF file to use')


def parse_node_args(args):
    '''Parse the standard OreSat Linux Node args.

    Parameters
    ----------
    args
        args from :py:func:`ArgumentParser.parse_args` to parse
    '''

    if args.verbose:
        level = 'DEBUG'
    else:
        level = 'INFO'

    logger.remove()
    if args.log:
        logger.add(SysLogHandler(address='/dev/log'), format=LOG_FORMAT, level=level)
    else:
        logger.add(sys.stderr, format=LOG_FORMAT, level=level)
