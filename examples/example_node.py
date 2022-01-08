'''Example Node'''

# following two lines are only here to be able to run using source code in repo
# remove them if oresat-linux-node is installed with pip
import sys
sys.path.append('..')

from oresat_linux_node.node import OreSatNode

example_node = OreSatNode('example_node.dcf', 'vcan0')

example_node.run()
