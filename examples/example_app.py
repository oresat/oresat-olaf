'''Example App'''

# following two lines are only here to be able to run using source code in repo
# remove them if oresat-app is installed with pip
import sys
sys.path.append('..')

from argparse import ArgumentParser

from olaf import app_args_parser, parse_app_args, App

# add the parent ArgumentParser for standard OreSat app args
parser = ArgumentParser(parents=[app_args_parser])
args = parser.parse_args()
parse_app_args(args)  # parse the standard app args

example_app = App('example_app.dcf', args.bus, args.node_id)

example_app.run()
