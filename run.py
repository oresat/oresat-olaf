#!/usr/bin/env python3

import os
from argparse import ArgumentParser

from olaf import app_args_parser, parse_app_args, app
from olaf.rest_api import rest_api

if __name__ == '__main__':

    parser = ArgumentParser(parents=[app_args_parser])
    args = parser.parse_args()
    parse_app_args(args)  # parse the standard app args

    eds_path = os.path.abspath(os.path.dirname(__file__)) + '/olaf/data/oresat_app.eds'
    app.setup(eds_path, args.bus, args.node_id, args.mock_hw)

    rest_api.start()
    app.run()
    rest_api.stop()
