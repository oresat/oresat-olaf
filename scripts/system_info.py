#!/usr/bin/env python3
'''System info script'''

from argparse import ArgumentParser
from os.path import dirname, abspath

import canopen

EDS_FILE = dirname(abspath(__file__)) + '/../oresat_linux_node.eds'
SYSTEM_INFO_INDEX = 0x3001

parser = ArgumentParser(description='System info')
parser.add_argument('bus', help='CAN bus to use')
parser.add_argument('node', help='device node name in hex')
args = parser.parse_args()

network = canopen.Network()
node = canopen.RemoteNode(int(args.node, 16), EDS_FILE)
network.add_node(node)
network.connect(bustype='socketcan', channel=args.bus)

print('')

os_name = node.sdo[SYSTEM_INFO_INDEX][1].phys
os_distro = node.sdo[SYSTEM_INFO_INDEX][2].phys
kernel_ver = node.sdo[SYSTEM_INFO_INDEX][3].phys
print('OS Name: ' + os_name)
print('OS Distro: ' + os_distro)
print('Kernel Version: ' + kernel_ver)

print('')

hostname = node.sdo[SYSTEM_INFO_INDEX][4].phys
uptime = node.sdo[SYSTEM_INFO_INDEX][5].phys
print('Hostname: ' + hostname)
print('Uptime: {} seconds'.format(uptime))

print('')

cpus = node.sdo[SYSTEM_INFO_INDEX][6].phys
cpu_arch = node.sdo[SYSTEM_INFO_INDEX][7].phys
cpu_gov = node.sdo[SYSTEM_INFO_INDEX][8].phys
cpu_freq = node.sdo[SYSTEM_INFO_INDEX][9].phys
print('CPU info')
print('  Total CPUs: {}'.format(cpus))
print('  Architecture ' + cpu_arch)
print('  CPU Frequency Governor {}'.format(cpu_gov))
print('  CPU Frequency {} MHz'.format(cpu_freq))

print('')

remote_procs = node.sdo[SYSTEM_INFO_INDEX][10].phys
if remote_procs == 0:
    print('No remote processors')
else:
    print('Remote processors')
    for i in range(remote_procs):
        node.sdo[SYSTEM_INFO_INDEX][11].phys = i
        rproc_name = node.sdo[SYSTEM_INFO_INDEX][12].phys
        rproc_state = node.sdo[SYSTEM_INFO_INDEX][13].phys
        print('  ' + rproc_name + ' is ' + rproc_state)

print('')

load_avg_1min = node.sdo[SYSTEM_INFO_INDEX][14].phys
load_avg_5min = node.sdo[SYSTEM_INFO_INDEX][15].phys
load_avg_15min = node.sdo[SYSTEM_INFO_INDEX][16].phys
print('Load averages')
print('  1min: {}'.format(load_avg_1min))
print('  5min: {}'.format(load_avg_5min))
print('  15min: {}'.format(load_avg_15min))

print('')

ram_total = node.sdo[SYSTEM_INFO_INDEX][17].phys
ram_free = node.sdo[SYSTEM_INFO_INDEX][18].phys
ram_shared = node.sdo[SYSTEM_INFO_INDEX][19].phys
ram_buffered = node.sdo[SYSTEM_INFO_INDEX][20].phys
ram_percent = node.sdo[SYSTEM_INFO_INDEX][21].phys
print('RAM')
print('  Total: {} MB'.format(ram_total))
print('  Free: {} MB'.format(ram_free))
print('  Shared: {} MB'.format(ram_shared))
print('  Buffered: {} MB'.format(ram_buffered))
print('  Usage: {} %'.format(ram_percent))

print('')

swap_total = node.sdo[SYSTEM_INFO_INDEX][22].phys
swap_free = node.sdo[SYSTEM_INFO_INDEX][23].phys
swap_percent = node.sdo[SYSTEM_INFO_INDEX][24].phys
print('Swap')
print('  Total: {}'.format(swap_total))
print('  Free: {}'.format(swap_free))
print('  Usage: {} %'.format(swap_percent))

print('')

procs = node.sdo[SYSTEM_INFO_INDEX][25].phys
print('Procs: {}'.format(procs))

print('')

root_part_total = node.sdo[SYSTEM_INFO_INDEX][26].phys
root_part_free = node.sdo[SYSTEM_INFO_INDEX][27].phys
root_part_percent = node.sdo[SYSTEM_INFO_INDEX][28].phys
print('Root Parition')
print('  Total: {} MB'.format(root_part_total))
print('  Free: {} MB'.format(root_part_free))
print('  Usage: {} %'.format(root_part_percent))

print('')

network.disconnect()
