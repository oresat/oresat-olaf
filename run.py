#!/usr/bin/env python3
"""Quick script to run olaf."""

from argparse import ArgumentParser

from olaf import olaf_parser, olaf_run, olaf_setup

if __name__ == "__main__":
    parser = ArgumentParser(parents=[olaf_parser])
    parser.add_argument("card", metavar="CARD", help="oresat card name; c3, star_tracker, etc")
    args = parser.parse_args()

    olaf_setup(args.card, args)
    olaf_run()
