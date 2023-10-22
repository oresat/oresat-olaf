#!/usr/bin/env python3

import sys
from argparse import ArgumentParser

from oresat_configs import OD_DB, NodeId, OreSatId

from olaf import app, logger, olaf_run, rest_api, logger_tmp_file_setup

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('card', metavar='CARD', help='oresat card name; c3, star_tracker_1, etc')
    parser.add_argument('-o', '--oresat', default='oresat0.5',
                        help='oresat mission; oresat0, oresat0.5')
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
    logger_tmp_file_setup(level)

    oresat_name = args.oresat.replace('.', '_').upper()
    oresat_id = OreSatId[oresat_name]

    card_name = args.card.upper().replace('-', '_')
    node_id = NodeId[card_name]

    od_db = OD_DB[oresat_id]
    od = od_db[node_id]
    if node_id == NodeId.C3:
        app.setup(od, args.bus, od_db)
    else:
        app.setup(od, args.bus)

    rest_api.setup(address=args.address, port=args.port)

    olaf_run()
