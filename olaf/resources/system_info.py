import os
import platform
from time import time

import canopen
import psutil

from ..common.resource import Resource

_B_TO_MB = 1024 * 1024


class SystemInfoResource(Resource):
    '''Resource for getting local system infomation'''

    def __init__(self, node: canopen.LocalNode):

        super().__init__(node, 'System Info', -1.0)

        self.index = 0x3001
        self.sub_os_distro = 0x1
        self.sub_os_name = 0x2
        self.sub_os_kernel_ver = 0x3
        self.sub_hostname = 0x4
        self.sub_uptime = 0x5
        self.sub_num_of_cpus = 0x6
        self.sub_cpu_arch = 0x7
        self.sub_cpu_gov = 0x8
        self.sub_cpu_freq = 0x9
        self.sub_num_of_rprocs = 0xA
        self.subrproc_iter = 0xB
        self.subrproc_name = 0xC
        self.subrproc_state = 0xD
        self.sub_load_avg_1min = 0xE
        self.sub_load_avg_5min = 0xF
        self.sub_load_avg_15min = 0x10
        self.sub_ram_total = 0x11
        self.sub_ram_free = 0x12
        self.sub_ram_shared = 0x13
        self.sub_ram_buffered = 0x14
        self.sub_ram_percent = 0x15
        self.sub_swap_total = 0x16
        self.sub_swap_free = 0x17
        self.sub_swap_percent = 0x18
        self.sub_procs = 0x19
        self.sub_root_part_total = 0x1A
        self.sub_root_part_free = 0x1B
        self.sub_root_part_percent = 0x1C

        self.rprocs = 0
        self.rproc_iter = 0

        with open('/etc/os-release', 'r') as f:
            os_release = f.readlines()

        obj = node.object_dictionary[self.index]
        obj[self.sub_os_distro].value = os_release[1].split('"')[1]
        obj[self.sub_os_name].value = platform.system()
        obj[self.sub_os_kernel_ver].value = platform.release()
        obj[self.sub_hostname].value = platform.node()
        obj[self.sub_num_of_cpus].value = psutil.cpu_count()
        obj[self.sub_cpu_arch].value = platform.machine()
        obj[self.sub_ram_total].value = psutil.virtual_memory().total // _B_TO_MB
        obj[self.sub_swap_total].value = psutil.swap_memory().total // _B_TO_MB
        obj[self.sub_root_part_total].value = psutil.disk_usage('/').total // _B_TO_MB
        self.rprocs = len(os.listdir('/sys/class/remoteproc'))  # save for `on_read`
        obj[self.sub_num_of_rprocs].value = self.rprocs

        node.add_read_callback(self.on_read)
        node.add_write_callback(self.on_write)

    def on_read(self, index, subindex, od):

        if index != self.index:
            return

        ret = None

        if subindex == self.sub_uptime:
            ret = int(time() - psutil.boot_time())
        elif subindex == self.sub_cpu_freq:
            ret = int(psutil.cpu_freq().current * 1000)
        elif subindex == self.subrproc_iter:
            ret = self.rproc_iter
        elif subindex == self.subrproc_name:
            file_path = '/sys/class/remoteproc/remoteproc' + str(self.rprocs) + '/state'
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    ret = f.read()
        elif subindex == self.subrproc_state:
            file_path = '/sys/class/remoteproc/remoteproc' + str(self.rprocs) + '/state'
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    ret = f.read()
        elif subindex == self.sub_load_avg_1min:
            ret = int(psutil.getloadavg()[0])
        elif subindex == self.sub_load_avg_5min:
            ret = int(psutil.getloadavg()[1])
        elif subindex == self.sub_load_avg_15min:
            ret = int(psutil.getloadavg()[2])
        elif subindex == self.sub_ram_free:
            ret = psutil.virtual_memory().free // _B_TO_MB
        elif subindex == self.sub_ram_shared:
            ret = psutil.virtual_memory().shared // _B_TO_MB
        elif subindex == self.sub_ram_buffered:
            ret = psutil.virtual_memory().buffers // _B_TO_MB
        elif subindex == self.sub_ram_percent:
            ret = psutil.virtual_memory().percent
        elif subindex == self.sub_swap_free:
            ret = psutil.swap_memory().free // _B_TO_MB
        elif subindex == self.sub_swap_percent:
            ret = psutil.swap_memory().percent
        elif subindex == self.sub_procs:
            ret = len(psutil.pids())
        elif subindex == self.sub_root_part_free:
            ret = psutil.disk_usage('/').free // _B_TO_MB
        elif subindex == self.sub_root_part_percent:
            ret = psutil.disk_usage('/').percent

        return ret

    def on_write(self, index, subindex, od, data):

        if index != self.index or subindex != self.subrproc_name:
            return

        temp = od.raw_decode(data)
        if temp < self.rprocs:
            self.rproc_iter = temp
