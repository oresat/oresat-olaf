import os
import sys
from logging.handlers import SysLogHandler
from argparse import ArgumentParser

from loguru import logger

from ._internals.app import app
from ._internals.rest_api import rest_api
from .common.resource import Resource
from .common.ecss import scet_int_from_time, scet_int_to_time, utc_int_from_time, utc_int_to_time
from .common.oresat_file import OreSatFile, new_oresat_file
from .common.oresat_file_cache import OreSatFileCache
from .common.timer_loop import TimerLoop

__version__ = '1.0.0'


def olaf_run(eds_path: str = None):
    '''Start the app and rest api.

    Parameters
    ----------
    eds_path: str
        The path to the eds or dcf file
    '''

    parser = ArgumentParser(prog='OLAF')
    parser.add_argument('-b', '--bus', default='vcan0', help='CAN bus to use, defaults to vcan0')
    parser.add_argument('-n', '--node-id', type=str, default='0', metavar='ID',
                        help='set the node ID')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose logging')
    parser.add_argument('-l', '--log', action='store_true', help='log to only journald')
    parser.add_argument('-e', '--eds', metavar='FILE', help='EDS/DCF file to use')
    parser.add_argument('-m', '--mock-hw', action='store_true', help='mock the hardware')
    parser.add_argument('-a', '--address', default='localhost', help='rest api address')
    parser.add_argument('-p', '--port', type=int, default=8000, help='rest api port number')
    args = parser.parse_args()

    if args.verbose:
        level = 'DEBUG'
    else:
        level = 'INFO'

    logger.remove()  # remove default logger
    if args.log:
        logger.add(SysLogHandler(address='/dev/log'), level=level)
    else:
        logger.add(sys.stdout, level=level)

    if eds_path is None:
        eds_path = args.eds

    app.setup(eds_path, args.bus, args.node_id, args.mock_hw)

    rest_api.start(address=args.address, port=args.port)
    app.run()
    rest_api.stop()
