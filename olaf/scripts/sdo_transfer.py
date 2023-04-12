#!/usr/bin/env python3
'''
SDO transfer script

This scipt act as CANopen master node, allowing it to read and write other
node's Object Dictionaries.
'''

import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from struct import pack, unpack
from enum import Enum, auto

import canopen


class CANopenTypes(Enum):
    '''All valid canopen types supported'''

    BOOLEAN = auto()
    INTEGER8 = auto()
    UNSIGNED8 = auto()
    INTEGER16 = auto()
    UNSIGNED16 = auto()
    INTEGER32 = auto()
    UNSIGNED32 = auto()
    INTEGER64 = auto()
    UNSIGNED64 = auto()
    REAL32 = auto()
    REAL64 = auto()
    VISABLE_STRING = auto()
    UNICODE_STRING = auto()
    OCTECT_STRING = auto()
    DOMAIN = auto()


NICE_NAMES = {
    CANopenTypes.BOOLEAN: ['b', 'bool', 'boolean'],
    CANopenTypes.INTEGER8: ['i8', 'int8', 'integer8'],
    CANopenTypes.UNSIGNED8: ['u8', 'uint8', 'unsiged8'],
    CANopenTypes.INTEGER16: ['i16', 'int16', 'integer16'],
    CANopenTypes.UNSIGNED16: ['u16', 'uint16', 'unsiged16'],
    CANopenTypes.INTEGER32: ['i32', 'int32', 'integer32'],
    CANopenTypes.UNSIGNED32: ['u32', 'uint32', 'unsiged32'],
    CANopenTypes.INTEGER64: ['i64', 'int64', 'integer64'],
    CANopenTypes.UNSIGNED64: ['u64', 'uint64', 'unsiged64'],
    CANopenTypes.REAL32: ['f32', 'float32', 'r32', 'real32'],
    CANopenTypes.REAL64: ['f64', 'float64', 'r64', 'real64'],
    CANopenTypes.VISABLE_STRING: ['s', 'string', 'v', 'visable_string'],
    CANopenTypes.UNICODE_STRING: ['u', 'unicode_string'],
    CANopenTypes.OCTECT_STRING: ['o', 'octets', 'octet_string'],
    CANopenTypes.DOMAIN: ['d', 'domain'],
}


DECODE_KEYS = {
    CANopenTypes.BOOLEAN: '?',
    CANopenTypes.INTEGER8: 'b',
    CANopenTypes.INTEGER16: 'h',
    CANopenTypes.INTEGER32: 'i',
    CANopenTypes.INTEGER64: 'q',
    CANopenTypes.UNSIGNED8: 'B',
    CANopenTypes.UNSIGNED16: 'H',
    CANopenTypes.UNSIGNED32: 'I',
    CANopenTypes.UNSIGNED64: 'Q',
    CANopenTypes.REAL32: 'f',
    CANopenTypes.REAL64: 'd',
}


EPILOG = 'DATA_TYPE options are (case insensitive): \n  ' \
    + '\n  '.join([', '.join(NICE_NAMES[i]) for i in NICE_NAMES])


def main():
    parser = ArgumentParser(
        description='read or write value to a node\'s object dictionary',
        formatter_class=RawDescriptionHelpFormatter,
        epilog=EPILOG
    )
    parser.add_argument('bus', metavar='BUS', help='CAN bus to use (e.g., can0, vcan0)')
    parser.add_argument('node', metavar='NODE', help='device node id in hex')
    parser.add_argument('mode', metavar='MODE', help='r[ead] or w[rite] (e.g. r, read, w, write)')
    parser.add_argument('index', metavar='INDEX',
                        help='object dictionary index in hex (e.g. 0x7000)')
    parser.add_argument('subindex', metavar='SUBINDEX',
                        help='object dictionary subindex in hex (e.g. 0x10)')
    parser.add_argument('data_type', metavar='DATA_TYPE', help='the data type, see list below')
    parser.add_argument('value', metavar='VALUE', nargs='?', default=0,
                        help='data to write or for only string/domain data types a path to a file '
                             '(e.g. file:data.txt)')
    args = parser.parse_args()

    for key in NICE_NAMES:
        if args.data_type.lower() in NICE_NAMES[key]:
            co_type = key
            break
    else:
        print(f'invalid data type "{args.data_type}"')
        sys.exit(1)

    # convert hex str to int
    index = int(args.index, 16)
    subindex = int(args.subindex, 16)

    # connect to network and add a fake node to make pythonic canopen happy
    network = canopen.Network()
    node = canopen.RemoteNode(int(args.node, 16), canopen.ObjectDictionary())
    network.add_node(node)
    network.connect(bustype='socketcan', channel=args.bus)

    if args.mode == 'r' or args.mode == 'read':
        try:
            raw_data = node.sdo.upload(index, subindex)
            network.disconnect()
        except Exception as e:
            print(e)
            network.disconnect()
            sys.exit(1)

        if co_type in DECODE_KEYS.keys():
            data = unpack(DECODE_KEYS[co_type], raw_data)[0]
        elif co_type == CANopenTypes.VISABLE_STRING:
            data = raw_data.decode('utf-8')
        elif co_type in [CANopenTypes.UNICODE_STRING, CANopenTypes.OCTECT_STRING,
                         CANopenTypes.DOMAIN]:
            data = raw_data

        print(data)
    elif args.mode == 'w' or args.mode == 'write':
        if co_type in [CANopenTypes.REAL32, CANopenTypes.REAL64]:
            raw_data = pack(DECODE_KEYS[co_type], float(args.value))
        elif co_type in DECODE_KEYS.keys():
            raw_data = pack(DECODE_KEYS[co_type], int(args.value))
        elif co_type in [CANopenTypes.VISABLE_STRING, CANopenTypes.UNICODE_STRING,
                         CANopenTypes.OCTECT_STRING, CANopenTypes.DOMAIN]:
            if args.value.startswith('file:'):
                with open(args.value[5:], 'rb') as f:
                    raw_data = f.read()
            else:
                raw_data = args.value

        try:
            node.sdo.download(index, subindex, raw_data)
            network.disconnect()
        except Exception as e:
            print(e)
            network.disconnect()
            sys.exit(1)
    else:
        print('invalid mode\nmust be "r", "read", "w", or "write"')
        sys.exit(1)


if __name__ == '__main__':
    main()
