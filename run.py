#!/usr/bin/env python3
"""Quick script to run olaf."""

import sys
from argparse import ArgumentParser

from oresat_configs import OreSatConfig, OreSatId

from olaf import app, logger, logger_tmp_file_setup, olaf_run, rest_api, __version__


def main():
    """Quick main to run a empty olaf app."""

    parser = ArgumentParser()
    parser.add_argument("card", metavar="CARD", help="oresat card name; c3, star_tracker_1, etc")
    parser.add_argument(
        "-o", "--oresat", default="oresat0.5", help="oresat mission; oresat0, oresat0.5"
    )
    parser.add_argument("-b", "--bus", default="vcan0", help="CAN bus to use, defaults to vcan0")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose logging")
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
    parser.add_argument("-w", "--hardware-version", default="0.0", help="set the hardware version")
    parser.add_argument("-n", "--number", type=int, default=1, help="card number")
    parser.add_argument(
        "-t",
        "--bus-type",
        default="socketcan",
        help="can bus type; can be socketcan or slcan",
    )
    args = parser.parse_args()

    if args.verbose:
        level = "DEBUG"
    else:
        level = "INFO"

    logger.remove()  # remove default logger
    logger.add(sys.stdout, level=level, backtrace=True)
    logger_tmp_file_setup(level)

    oresat_name = args.oresat.replace(".", "_").upper()
    oresat_id = OreSatId[oresat_name]

    card_name = args.card.lower().replace("-", "_")

    config = OreSatConfig(oresat_id)

    if card_name not in config.cards:
        card_name += f"_{args.number}"
    if card_name not in config.cards:
        print(f"invalid card {args.card} for {args.oresat}")
        sys.exit(1)

    od = config.od_db[card_name]

    od["versions"]["olaf_version"].value = __version__
    if args.hardware_version != "0.0":
        od["versions"]["hw_version"].value = args.hardware_version

    is_octavo = config.cards[card_name].processor == "octavo"

    if card_name == "c3":
        app.setup(od, args.bus, args.bus_type, config.od_db, is_octavo)
    else:
        app.setup(od, args.bus, args.bus_type, None, is_octavo)

    rest_api.setup(address=args.address, port=args.port)

    olaf_run()


if __name__ == "__main__":
    main()
