'''Example Node'''

# following two lines are only here to be able to run using source code in repo
# remove them if oresat-linux-node is installed with pip
import sys
sys.path.append('..')

from argparse import ArgumentParser

from oresat_linux_node import node_args_parser, parse_node_args
from oresat_linux_node.node import OreSatNode

# add OreSat Linux Node parent ArgumentParser for standard node args
parser = ArgumentParser(parents=[node_args_parser])
args = parser.parse_args()
parse_node_args(args)  # parse the standard node args

example_node = OreSatNode('example_node.dcf', args.bus, args.node_id)

example_node.run()
