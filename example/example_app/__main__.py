'''Example App'''

from os.path import dirname, abspath
from argparse import ArgumentParser

from olaf import app_args_parser, parse_app_args, App

if __name__ == '__main__':

    # add the parent ArgumentParser for standard OreSat app args
    parser = ArgumentParser(parents=[app_args_parser])
    # add any other args here
    args = parser.parse_args()
    parse_app_args(args)  # parse the standard app args

    example_app = App(dirname(abspath(__file__)) + '/example_app.dcf', args.bus, args.node_id)

    # add resources as needed

    example_app.run()
