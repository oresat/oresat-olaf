import os
import sys
from logging.handlers import SysLogHandler
from argparse import ArgumentParser, Namespace

import canopen
from loguru import logger
from oresat_configs import OreSatId, NodeId, OreSatConfig

from ._internals.app import app, App
from ._internals.node import Node, NodeStop, NetworkError
from ._internals.master_node import MasterNode
from ._internals.rest_api import rest_api, RestAPI, render_olaf_template
from ._internals.services.logs import logger_tmp_file_setup
from .common.resource import Resource
from .common.service import Service
from .common.ecss import scet_int_from_time, scet_int_to_time, utc_int_from_time, utc_int_to_time
from .common.oresat_file import OreSatFile, new_oresat_file
from .common.oresat_file_cache import OreSatFileCache
from .common.timer_loop import TimerLoop
from .common.gpio import Gpio, GpioError, GPIO_LOW, GPIO_HIGH, GPIO_IN, GPIO_OUT
from .common.adc import Adc
from .common.daemon import Daemon, DaemonState
from .common.cpufreq import get_cpufreq, get_cpufreq_gov, set_cpufreq, set_cpufreq_gov, A8_CPUFREQS
from .common.pru import Pru, PruState, PruError


__version__ = '3.0.0'


def olaf_setup(node_id: NodeId) -> (Namespace, dict):
    '''
    Parse runtime args and setup the app and REST API.

    Parameters
    ----------
    node: Node
        The card's node

    Returns
    -------
    Namespace
        The runtime args.
    dict
        The OreSat configs.
    '''

    parser = ArgumentParser(prog='OLAF')
    parser.add_argument('-b', '--bus', default='vcan0', help='CAN bus to use, defaults to vcan0')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose logging')
    parser.add_argument('-l', '--log', action='store_true', help='log to only journald')
    parser.add_argument('-m', '--mock-hw', nargs='*', metavar='HW', default=[],
                        help='list the hardware to mock or just "all" to mock all hardware')
    parser.add_argument('-a', '--address', default='localhost',
                        help='rest api address, defaults to localhost')
    parser.add_argument('-p', '--port', type=int, default=8000,
                        help='rest api port number, defaults to 8000')
    parser.add_argument('-d', '--disable-flight-mode', action='store_true',
                        help='disable flight mode on start, defaults to flight mode enabled')
    parser.add_argument('-o', '--oresat', default='oresat0.5',
                        help='oresat mission; oresat0, oresat0.5, etc')
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

    logger_tmp_file_setup(level)

    arg_oresat = args.oresat.lower()
    if arg_oresat in ['oresat0', '0']:
        oresat_id = OreSatId.ORESAT0
    elif arg_oresat in ['oresat0.5', 'oresat0_5', '0.5']:
        oresat_id = OreSatId.ORESAT0_5
    elif arg_oresat in ['oresat', '1']:
        oresat_id = OreSatId.ORESAT1
    else:
        raise ValueError(f'invalid oresat mission {args.oresat}')

    config = OreSatConfig(oresat_id)
    od = config.od_db[node_id]

    if args.disable_flight_mode:
        od['flight_mode'].value = False

    od['versions']['olaf_version'].value = __version__

    if node_id == NodeId.C3:
        app.setup(od, args.bus, config.od_db)
    else:
        app.setup(od, args.bus)

    rest_api.setup(address=args.address, port=args.port)

    return args, config


def olaf_run():
    '''Start the app and REST API.'''

    rest_api.start()
    app.run()
    rest_api.stop()
