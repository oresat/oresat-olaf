import sys
from logging.handlers import SysLogHandler
from argparse import ArgumentParser

from loguru import logger

# public api here
from .app import App
from .common.resource import Resource
from .common.ecss import scet_int_from_time, scet_int_to_time, utc_int_from_time, utc_int_to_time
from .common.oresat_file import OreSatFile, new_oresat_file
from .common.oresat_file_cache import OreSatFileCache
from .common.pru import PRU, PRUError, PRUState

__version__ = '0.3.0'

app_args_parser = ArgumentParser(add_help=False)
'''The optional, but recommend **parent** :py:class:`ArgumentParser` object to use.'''

app_args_parser.add_argument('-b', '--bus', default='vcan0',
                             help='CAN bus to use, defaults to vcan0')
app_args_parser.add_argument('-n', '--node-id', type=str, default='0', metavar='ID',
                             help='set the node ID')
app_args_parser.add_argument('-v', '--verbose', action='store_true', help='verbose logging')
app_args_parser.add_argument('-l', '--log', action='store_true', help='log to only journald')
app_args_parser.add_argument('-e', '--eds', metavar='FILE', help='EDS/DCF file to use')
app_args_parser.add_argument('-m', '--mock-hw', action='store_true', help='mock the hardware')


def parse_app_args(args):
    '''Parse the standard OreSat Linux App args.

    Parameters
    ----------
    args
        args from :py:func:`ArgumentParser.parse_args` to parse
    '''

    if args.verbose:
        level = 'DEBUG'
    else:
        level = 'INFO'

    logger.remove()  # remove default logger
    if args.log:
        logger.add(SysLogHandler(address='/dev/log'), level=level)
    else:
        logger.add(sys.stdout, level=level)
