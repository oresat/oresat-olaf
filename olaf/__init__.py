"""OLAF (OreSat Linux App Framework)"""

import os
import sys
from argparse import ArgumentParser, Namespace
from logging.handlers import SysLogHandler

import canopen
from loguru import logger
from oresat_configs import NodeId, OreSatConfig, OreSatId

from ._internals.app import App, app
from ._internals.master_node import MasterNode
from ._internals.node import NetworkError, Node, NodeStop
from ._internals.rest_api import RestAPI, render_olaf_template, rest_api
from ._internals.services.logs import logger_tmp_file_setup
from .common.adc import Adc
from .common.cpufreq import A8_CPUFREQS, get_cpufreq, get_cpufreq_gov, set_cpufreq, set_cpufreq_gov
from .common.daemon import Daemon, DaemonState
from .common.ecss import scet_int_from_time, scet_int_to_time, utc_int_from_time, utc_int_to_time
from .common.gpio import GPIO_HIGH, GPIO_IN, GPIO_LOW, GPIO_OUT, Gpio, GpioError
from .common.oresat_file import OreSatFile, new_oresat_file
from .common.oresat_file_cache import OreSatFileCache
from .common.pru import Pru, PruError, PruState
from .common.resource import Resource
from .common.service import Service, ServiceState
from .common.timer_loop import TimerLoop

__version__ = "3.2.0"


def olaf_setup(name: str) -> tuple[Namespace, dict]:
    """
    Parse runtime args and setup the app and REST API.

    Parameters
    ----------
    name: str
        The card's node name.

    Returns
    -------
    Namespace
        The runtime args.
    dict
        The OreSat configs.
    """

    # for backwards support
    if name == NodeId.CFC:
        name = "cfc_processor"
    elif isinstance(name, NodeId):
        name = name.name.lower()

    parser = ArgumentParser(prog="OLAF")
    parser.add_argument("-b", "--bus", default="vcan0", help="CAN bus to use, defaults to vcan0")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose logging")
    parser.add_argument("-l", "--log", action="store_true", help="log to only journald")
    parser.add_argument(
        "-m",
        "--mock-hw",
        nargs="*",
        metavar="HW",
        default=[],
        help='list the hardware to mock or just "all" to mock all hardware',
    )
    parser.add_argument(
        "-a", "--address", default="localhost", help="rest api address, defaults to localhost"
    )
    parser.add_argument(
        "-p", "--port", type=int, default=8000, help="rest api port number, defaults to 8000"
    )
    parser.add_argument(
        "-d",
        "--disable-flight-mode",
        action="store_true",
        help="disable flight mode on start, defaults to flight mode enabled",
    )
    parser.add_argument(
        "-o", "--oresat", default="oresat0.5", help="oresat mission; oresat0, oresat0.5, etc"
    )
    parser.add_argument("-n", "--number", type=int, default=1, help="card number")
    args = parser.parse_args()

    if args.verbose:
        level = "DEBUG"
    else:
        level = "INFO"

    logger.remove()  # remove default logger
    if args.log:
        logger.add(SysLogHandler(address="/dev/log"), level=level, backtrace=True)
    else:
        logger.add(sys.stdout, level=level, backtrace=True)

    logger_tmp_file_setup(level)

    arg_oresat = args.oresat.lower()
    if arg_oresat in ["oresat0", "0"]:
        oresat_id = OreSatId.ORESAT0
    elif arg_oresat in ["oresat0.5", "oresat0_5", "0.5"]:
        oresat_id = OreSatId.ORESAT0_5
    elif arg_oresat in ["oresat", "oresat1", "1"]:
        oresat_id = OreSatId.ORESAT1
    else:
        raise ValueError(f"invalid oresat mission {args.oresat}")

    config = OreSatConfig(oresat_id)

    if name not in config.cards:
        name += f"_{args.number}"
    if name not in config.cards:
        raise ValueError(f"invalid card {name} for {args.oresat}")

    od = config.od_db[name]

    if args.disable_flight_mode:
        od["flight_mode"].value = False

    od["versions"]["olaf_version"].value = __version__

    is_octavo = config.cards[name].processor == "octavo"

    if name == "c3":
        app.setup(od, args.bus, config.od_db, is_octavo)
    else:
        app.setup(od, args.bus, None, is_octavo)

    rest_api.setup(address=args.address, port=args.port)

    return args, config


def olaf_run():
    """Start the app and REST API."""

    rest_api.start()
    app.run()
    rest_api.stop()
