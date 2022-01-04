import sys
sys.path.append('..')

from oresat_linux_node.node import OreSatNode

example_node = OreSatNode('example_node.dcf', 'vcan0')

try:
    example_node.run()
except KeyboardInterrupt:
    example_node.stop()
except Exception as exc:
    print(exc)
    example_node.stop()
