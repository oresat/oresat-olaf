#!/usr/bin/env python3
'''System info script'''

from argparse import ArgumentParser
from os.path import dirname, abspath

import canopen

EDS_FILE = dirname(abspath(__file__)) + '/../_internals/data/oresat_app.eds'
SYSTEM_INFO_INDEX = 0x3001


def main():
    parser = ArgumentParser(description='System info')
    parser.add_argument('bus', help='CAN bus to use')
    parser.add_argument('node', help='device node name in hex')
    args = parser.parse_args()

    network = canopen.Network()
    node = canopen.RemoteNode(int(args.node, 16), EDS_FILE)
    network.add_node(node)
    network.connect(bustype='socketcan', channel=args.bus)

    try:
        system_info_record = node.sdo[SYSTEM_INFO_INDEX]
    except Exception as exc:
        print(exc)
        return

    print('')

    os_name = system_info_record[1].phys
    os_distro = system_info_record[2].phys
    kernel_ver = system_info_record[3].phys
    print(f'OS Name: {os_name}')
    print(f'OS Distro: {os_distro}')
    print(f'Kernel Version: {kernel_ver}')

    print('')

    hostname = system_info_record[4].phys
    uptime = system_info_record[5].phys
    print(f'Hostname: {hostname}')
    print(f'Uptime: {uptime} seconds')

    print('')

    cpus = system_info_record[6].phys
    cpu_arch = system_info_record[7].phys
    cpu_gov = system_info_record[8].phys
    cpu_freq = system_info_record[9].phys
    print('CPU info')
    print(f'  Total CPUs: {cpus}')
    print(f'  Architecture: {cpu_arch}')
    print(f'  CPU Frequency Governor: {cpu_gov}')
    print(f'  CPU Frequency: {cpu_freq} MHz')

    print('')

    remote_procs = system_info_record[10].phys
    if remote_procs == 0:
        print('No remote processors')
    else:
        print('Remote processors')
        for i in range(remote_procs):
            system_info_record[11].phys = i
            rproc_name = system_info_record[12].phys
            rproc_state = system_info_record[13].phys
            print(f'  {rproc_name} is {rproc_state}')

    print('')

    load_avg_1min = system_info_record[14].phys
    load_avg_5min = system_info_record[15].phys
    load_avg_15min = system_info_record[16].phys
    print('Load averages')
    print(f'  1min: {load_avg_1min}')
    print(f'  5min: {load_avg_5min}')
    print(f'  15min: {load_avg_15min}')

    print('')

    ram_total = system_info_record[17].phys
    ram_free = system_info_record[18].phys
    ram_shared = system_info_record[19].phys
    ram_buffered = system_info_record[20].phys
    ram_percent = system_info_record[21].phys
    print('RAM')
    print(f'  Total: {ram_total} MB')
    print(f'  Free: {ram_free} MB')
    print(f'  Shared: {ram_shared} MB')
    print(f'  Buffered: {ram_buffered} MB')
    print(f'  Usage: {ram_percent} %')

    print('')

    swap_total = system_info_record[22].phys
    swap_free = system_info_record[23].phys
    swap_percent = system_info_record[24].phys
    print('Swap')
    print(f'  Total: {swap_total}')
    print(f'  Free: {swap_free}')
    print(f'  Usage: {swap_percent} %')

    print('')

    procs = system_info_record[25].phys
    print(f'Procs: {procs}')

    print('')

    root_part_total = system_info_record[26].phys
    root_part_free = system_info_record[27].phys
    root_part_percent = system_info_record[28].phys
    print('Root Parition')
    print('  Total: {} MB'.format(root_part_total))
    print('  Free: {} MB'.format(root_part_free))
    print('  Usage: {} %'.format(root_part_percent))

    print('')

    network.disconnect()


if __name__ == '__main__':
    main()
