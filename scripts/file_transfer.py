#!/usr/bin/env python3
'''OLAF file transfer script'''

import sys
from argparse import ArgumentParser
from os.path import basename, dirname, abspath

import canopen

EDS_FILE = dirname(abspath(__file__)) + '/../oresat_app.eds'

# valid cache selector inputs
FREAD_CACHE = 0
FWRITE_CACHE = 1
FCACHE_INDEX = 0x3002


def main():
    parser = ArgumentParser(description='OLM file transfer')
    parser.add_argument('bus', help='CAN bus to use')
    parser.add_argument('node', help='device node name in hex')
    parser.add_argument('-l', '--list', dest='cache', default=None,
                        help='list files in cache, where CACHE is fread or fwrite')
    parser.add_argument('-r', '--read', dest='read_file',
                        help='read file from OLM fread cache')
    parser.add_argument('-w', '--write', dest='write_file',
                        help='write file to OLM')

    args = parser.parse_args()
    network = canopen.Network()
    node = canopen.RemoteNode(int(args.node, 16), EDS_FILE)
    network.add_node(node)
    network.connect(bustype='socketcan', channel=args.bus)

    if args.cache is not None:
        if args.cache == 'fread':
            node.sdo[FCACHE_INDEX][3].phys = FREAD_CACHE
        elif args.cache == 'fwrite':
            node.sdo[FCACHE_INDEX][3].phys = FWRITE_CACHE
        else:
            print('invalid cache')
            sys.exit(1)

        node.sdo[FCACHE_INDEX][4].raw = b'\00'  # clear filter

        for i in range(node.sdo[FCACHE_INDEX][5].phys):
            node.sdo[FCACHE_INDEX][6].phys = i
            print(node.sdo[FCACHE_INDEX][7].phys)
    elif args.read_file is not None:
        node.sdo[0x3003][1].raw = args.read_file.encode('utf-8')
        infile = node.sdo[0x3003][2].open('rb', encoding='ascii')
        outfile = open(args.read_file, 'wb')
        outfile.writelines(infile)

        infile.close()
        outfile.close()
    elif args.write_file is not None:
        node.sdo[0x3004][1].raw = basename(args.write_file).encode('utf-8')
        with open(args.write_file, 'rb') as fptr:
            file_data = fptr.read()
        node.sdo[0x3004][2].raw = file_data
    else:
        print('invalid mode')
        sys.exit(1)

    network.disconnect()


if __name__ == '__main__':
    main()
