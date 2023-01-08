#!/usr/bin/env python3
'''Generate a new OLAF app EDS file script'''

from argparse import ArgumentParser
from os.path import dirname, abspath
from datetime import datetime

EDS_FILE = dirname(abspath(__file__)) + '/../_internals/data/oresat_app.eds'


def _replace_value(lines: list, key: str, value: str):
    for i in range(50):
        if lines[i].startswith(key):
            lines[i] = f'{key}={value}\n'
            break


def main():
    parser = ArgumentParser(description='Make a new OLAF app EDS file')
    parser.add_argument('filename', help='the name of the eds file to make')
    parser.add_argument('-d', '--description', default='', help='set the description in eds')
    parser.add_argument('-c', '--creator-name', default='', help='set the creator\'s name in eds')
    parser.add_argument('-v', '--vendor-name', default='', help='set the vendor\'s name in eds')
    parser.add_argument('-p', '--product-name', default='', help='set the product name in eds')
    args = parser.parse_args()

    with open(EDS_FILE, 'r') as f:
        lines = f.readlines()

    dt = datetime.now()
    t_str = dt.strftime('%I:%M%p')
    d_str = dt.strftime('%m-%d-%Y')

    _replace_value(lines, 'FileName', args.filename)
    _replace_value(lines, 'Description', args.description)
    _replace_value(lines, 'CreatedBy', args.creator_name)
    _replace_value(lines, 'CreationTime', t_str)
    _replace_value(lines, 'CreationDate', d_str)
    _replace_value(lines, 'ModifiedBy', args.creator_name)
    _replace_value(lines, 'ModificationTime', t_str)
    _replace_value(lines, 'ModificationDate', d_str)
    _replace_value(lines, 'VendorName', args.vendor_name)
    _replace_value(lines, 'ProductName', args.product_name)

    with open(args.filename, 'w') as f:
        f.writelines(lines)


if __name__ == '__main__':
    main()
