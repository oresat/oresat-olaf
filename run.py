#!/usr/bin/env python3

from argparse import ArgumentParser

from olaf import app_args_parser, parse_app_args, App

if __name__ == '__main__':

    parser = ArgumentParser(parents=[app_args_parser])
    args = parser.parse_args()
    parse_app_args(args)  # parse the standard app args

    app = App('olaf/data/oresat_app.eds', args.bus, args.node_id)

    exit(app.run())
