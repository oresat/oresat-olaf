#!/usr/bin/env python3
'''CANopen send SYNC script'''

from argparse import ArgumentParser

import canopen


def main():
    parser = ArgumentParser(description='send a SYNC message')
    parser.add_argument('bus', help='CAN bus to use')

    args = parser.parse_args()
    network = canopen.Network()
    network.connect(bustype='socketcan', channel=args.bus)

    network.sync.transmit()

    network.disconnect()


if __name__ == '__main__':
    main()
