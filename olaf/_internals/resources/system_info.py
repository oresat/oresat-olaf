import os
import platform
from time import time
from enum import IntEnum, auto

import psutil

from ...common.resource import Resource

_B_TO_MB = 1024 * 1024


class Subindex(IntEnum):
    OS_NAME = auto()
    OS_DISTRO = auto()
    OS_KERNEL_VER = auto()
    HOSTNAME = auto()
    UPTIME = auto()
    NUM_OF_CPUS = auto()
    CPU_ARCH = auto()
    CPU_GOV = auto()
    CPU_FREQ = auto()
    NUM_OF_RPROCS = auto()
    RPROC_ITER = auto()
    RPROC_NAME = auto()
    RPROC_STATE = auto()
    LOAD_AVG_1MIN = auto()
    LOAD_AVG_5MIN = auto()
    LOAD_AVG_15MIN = auto()
    RAM_TOTAL = auto()
    RAM_FREE = auto()
    RAM_SHARED = auto()
    RAM_BUFFERED = auto()
    RAM_PERCENT = auto()
    SWAP_TOTAL = auto()
    SWAP_FREE = auto()
    SWAP_PERCENT = auto()
    PROCS = auto()
    ROOT_PART_TOTAL = auto()
    ROOT_PART_FREE = auto()
    ROOT_PART_PERCENT = auto()


class SystemInfoResource(Resource):
    '''Resource for getting local system infomation'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.index = 0x3001
        self.rprocs = 0
        self.rproc_iter = 0

    def on_start(self):

        with open('/etc/os-release', 'r') as f:
            os_release = f.readlines()

        si_record = self.od[self.index]
        si_record[Subindex.OS_NAME.value].value = platform.system()
        si_record[Subindex.OS_DISTRO.value].value = os_release[1].split('"')[1]
        si_record[Subindex.OS_KERNEL_VER.value].value = platform.release()
        si_record[Subindex.HOSTNAME.value].value = platform.node()
        si_record[Subindex.NUM_OF_CPUS.value].value = psutil.cpu_count()
        si_record[Subindex.CPU_ARCH.value].value = platform.machine()
        si_record[Subindex.RAM_TOTAL.value].value = psutil.virtual_memory().total // _B_TO_MB
        si_record[Subindex.SWAP_TOTAL.value].value = psutil.swap_memory().total // _B_TO_MB
        si_record[Subindex.ROOT_PART_TOTAL.value].value = psutil.disk_usage('/').total // _B_TO_MB
        if os.path.isdir('/sys/class/remoteproc'):
            self.rprocs = len(os.listdir('/sys/class/remoteproc'))
            # save for `on_read`
        si_record[Subindex.NUM_OF_RPROCS.value].value = self.rprocs

    def on_read(self, index, subindex, od):

        if index != self.index:
            return

        ret = None

        if subindex == Subindex.UPTIME.value:
            ret = int(time() - psutil.boot_time())
        elif subindex == Subindex.CPU_GOV.value:
            file_path = '/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor'
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    ret = f.read().strip()
        elif subindex == Subindex.CPU_FREQ.value:
            # there was MHz vs GHz bug with psutil v5.9.0
            ret = int(psutil.cpu_freq().current)
            if ret < 10:  # value was in GHz, not MHz
                ret = int(psutil.cpu_freq().current * 1000)
        elif subindex == Subindex.RPROC_ITER.value:
            ret = self.rproc_iter
        elif subindex == Subindex.RPROC_NAME.value:
            file_path = f'/sys/class/remoteproc/remoteproc{self.rprocs}/state'
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    ret = f.read()
        elif subindex == Subindex.RPROC_STATE.value:
            file_path = f'/sys/class/remoteproc/remoteproc{self.rprocs}/state'
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    ret = f.read()
        elif subindex == Subindex.LOAD_AVG_1MIN.value:
            ret = int(psutil.getloadavg()[0] * 100)
        elif subindex == Subindex.LOAD_AVG_5MIN.value:
            ret = int(psutil.getloadavg()[1] * 100)
        elif subindex == Subindex.LOAD_AVG_15MIN.value:
            ret = int(psutil.getloadavg()[2] * 100)
        elif subindex == Subindex.RAM_FREE.value:
            ret = psutil.virtual_memory().free // _B_TO_MB
        elif subindex == Subindex.RAM_SHARED.value:
            ret = psutil.virtual_memory().shared // _B_TO_MB
        elif subindex == Subindex.RAM_BUFFERED.value:
            ret = psutil.virtual_memory().buffers // _B_TO_MB
        elif subindex == Subindex.RAM_PERCENT.value:
            ret = psutil.virtual_memory().percent
        elif subindex == Subindex.SWAP_FREE.value:
            ret = psutil.swap_memory().free // _B_TO_MB
        elif subindex == Subindex.SWAP_PERCENT.value:
            ret = psutil.swap_memory().percent
        elif subindex == Subindex.PROCS.value:
            ret = len(psutil.pids())
        elif subindex == Subindex.ROOT_PART_FREE.value:
            ret = psutil.disk_usage('/').free // _B_TO_MB
        elif subindex == Subindex.ROOT_PART_PERCENT.value:
            ret = psutil.disk_usage('/').percent

        return ret

    def on_write(self, index, subindex, od, data):

        if index != self.index or subindex != Subindex.RPROC_ITER.value:
            return

        temp = od.decode_raw(data)
        if temp < self.rprocs:
            self.rproc_iter = temp
