import os
import sys
from logging.handlers import SysLogHandler
from argparse import ArgumentParser, Namespace

from loguru import logger

from ._internals.app import app, App
from ._internals.node import Node, NodeStop, NetworkError
from ._internals.master_node import MasterNode
from ._internals.rest_api import rest_api, RestAPI, render_olaf_template
from .common.resource import Resource
from .common.ecss import scet_int_from_time, scet_int_to_time, utc_int_from_time, utc_int_to_time
from .common.oresat_file import OreSatFile, new_oresat_file
from .common.oresat_file_cache import OreSatFileCache
from .common.timer_loop import TimerLoop
from .common.gpio import GPIO

__version__ = '2.1.0'


def olaf_setup(eds_path: str = None, master_node: bool = False) -> Namespace:
    '''
    Parse runtime args and setup the app and REST API.

    Parameters
    ----------
    eds_path: str
        The path to the eds or dcf file.
    master_node: bool
        Run as master node.

    Returns
    -------
    Namespace
        The runtime args.
    '''

    parser = ArgumentParser(prog='OLAF')
    parser.add_argument('-b', '--bus', default='vcan0', help='CAN bus to use, defaults to vcan0')
    parser.add_argument('-n', '--node-id', type=str, default='0', metavar='ID',
                        help='set the node ID')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose logging')
    parser.add_argument('-l', '--log', action='store_true', help='log to only journald')
    parser.add_argument('-e', '--eds', metavar='FILE', help='EDS / DCF file to use')
    parser.add_argument('-m', '--mock-hw', nargs='*', metavar='HW', default=[],
                        help='list the hardware to mock or just "all" to mock all hardware')
    parser.add_argument('-a', '--address', default='localhost',
                        help='rest api address, defaults to localhost')
    parser.add_argument('-p', '--port', type=int, default=8000,
                        help='rest api port number, defaults to 8000')
    args = parser.parse_args()

    if args.verbose:
        level = 'DEBUG'
    else:
        level = 'INFO'

    logger.remove()  # remove default logger
    if args.log:
        logger.add(SysLogHandler(address='/dev/log'), level=level, backtrace=True)
    else:
        logger.add(sys.stdout, level=level, backtrace=True)

    olaf_boot_logs = '/tmp/olaf.log'
    if os.path.isfile(olaf_boot_logs):
        os.remove(olaf_boot_logs)
    logger.add(olaf_boot_logs, level=level, backtrace=True)

    if eds_path is None:
        eds_path = args.eds

    app.setup(eds_path, args.bus, args.node_id, master_node=master_node)
    rest_api.setup(address=args.address, port=args.port)

    return args


def olaf_run():
    '''Start the app and REST API.'''

    rest_api.start()
    app.run()
    rest_api.stop()
