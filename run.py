#!/usr/bin/env python3

import os
import sys
from argparse import ArgumentParser

from oresat_od_db import NodeId
from oresat_od_db.oresat0_5 import C3_OD, OD_DB

from olaf import app, logger, olaf_run, rest_api

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('card', metavar='CARD', help='oresat card name; c3, star_tracker_1, etc')
    parser.add_argument('-o', '--oresat', default=0.5, type=float, help='oresat#')
    parser.add_argument('-b', '--bus', default='vcan0', help='CAN bus to use, defaults to vcan0')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose logging')
    parser.add_argument('-a', '--address', default='localhost',
                        help='rest api address, defaults to localhost')
    parser.add_argument('-p', '--port', type=int, default=8000,
                        help='rest api port number, defaults to 8000')
    parser.add_argument('-d', '--disable-flight-mode', action='store_true',
                        help='disable flight mode on start, defaults to flight mode enabled')
    args = parser.parse_args()

    if args.verbose:
        level = 'DEBUG'
    else:
        level = 'INFO'

    logger.remove()  # remove default logger
    logger.add(sys.stdout, level=level, backtrace=True)

    # log file for log service (overrides each time app starts)
    olaf_boot_logs = '/tmp/olaf.log'
    if os.path.isfile(olaf_boot_logs):
        os.remove(olaf_boot_logs)
    logger.add(olaf_boot_logs, level=level, backtrace=True)

    card_name = args.card.upper().replace('-', '_')
    node_id = NodeId[card_name]
    od = OD_DB[node_id]
    if od == C3_OD:
        app.setup(od, args.bus, OD_DB)
    else:
        app.setup(od, args.bus)

    rest_api.setup(address=args.address, port=args.port)

    olaf_run()
