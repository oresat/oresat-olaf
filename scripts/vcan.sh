#!/bin/bash

user=`id -u`
if [ $user -ne 0 ]; then 
    echo "Run as root"
    exit
fi

if [ $# -eq 0 ]; then
    vcan_status=`ip a | grep vcan0`
    if [ -z "$vcan_status" ]; then
        ip link add dev vcan0 type vcan
        ip link set vcan0 up
    fi
else
    if [ $1 == "disable" ]; then
        ip link set vcan0 down
        ip link del dev vcan0
    fi
fi
