#!/usr/bin/env python3
'''OS command script'''

from time import sleep
from argparse import ArgumentParser
from os.path import dirname, abspath

import canopen


EDS_FILE = dirname(abspath(__file__)) + '/../_internals/data/oresat_app.eds'
OS_COMMAND_INDEX = 0x1023


def main():
    parser = ArgumentParser(description='Send bash command over CAN bus')
    parser.add_argument('bus', help='CAN bus to use')
    parser.add_argument('node', help='device node name in hex')
    parser.add_argument('command', nargs='?', help='bash command to run, must in \
    inside of \'\'')
    args = parser.parse_args()

    network = canopen.Network()
    node = canopen.RemoteNode(int(args.node, 16), EDS_FILE)
    network.add_node(node)
    network.connect(bustype='socketcan', channel=args.bus)

    try:
        node.sdo[OS_COMMAND_INDEX][1].raw = args.command.encode('utf-8')
    except Exception as exc:
        print(exc)
        return

    while node.sdo[OS_COMMAND_INDEX][2].phys == 0xFF:
        sleep(0.1)

    print('status: ' + hex(node.sdo[OS_COMMAND_INDEX][2].phys))
    print('reply:\n\n' + node.sdo[OS_COMMAND_INDEX][3].raw.decode('utf-8'))

    network.disconnect()


if __name__ == '__main__':
    main()
