#!/usr/bin/env python3

from argparse import ArgumentParser

from olaf import app_args_parser, parse_app_args, app
from olaf.rest_api import rest_api

if __name__ == '__main__':

    parser = ArgumentParser(parents=[app_args_parser])
    args = parser.parse_args()
    parse_app_args(args)  # parse the standard app args

    rest_api.start()
    app.run()
    rest_api.stop()
