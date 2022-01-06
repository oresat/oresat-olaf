'''App for monitoring the local system'''

import platform
from time import time

import canopen
import psutil

from ..common.app import App

B_TO_MB = 1024 * 1024


class SystemInfoApp(App):

    def __init__(self, node: canopen.LocalNode):
        super().__init__('System Info', 10.0)

        self.node = node
        self.index = 0x3001

    def setup(self):

        self.node.add_read_callback(self.on_read)

        with open('/etc/os-release', 'r') as fptr:
            os_release = fptr.readlines()

        obj = self.node.object_dictionary[self.index]

        obj['OS distro'].value = os_release[1].split('"')[1]
        obj['OS name'].value = platform.system()
        obj['OS kernel version'].value = platform.release()
        obj['hostname'].value = platform.node()
        obj['Number of CPUs'].value = psutil.cpu_count()
        obj['CPU architecture'].value = platform.machine()
        obj['Ram total'].value = psutil.virtual_memory().total // B_TO_MB
        obj['Swap total'].value = psutil.swap_memory().total // B_TO_MB
        obj['Root partition total'].value = psutil.disk_usage('/').total // B_TO_MB

    def on_loop(self):
        obj = self.node.object_dictionary[self.index]

        obj['Root partition percent'].value = int(psutil.disk_usage('/').percent)
        obj['Ram percent'].value = psutil.virtual_memory().percent

    def on_read(self, index, subindex, od):
        '''Callback for a SDO read from the system info object'''

        obj = od

        if index != self.index:
            return

        if obj.name == 'CPU frequency':
            value = int(psutil.cpu_freq().current)
        elif obj.name == 'Uptime':
            value = int(time() - psutil.boot_time())
        elif obj.name == 'Load average 1min':
            value = int(psutil.getloadavg()[0])
        elif obj.name == 'Load average 5min':
            value = int(psutil.getloadavg()[1])
        elif obj.name == 'Load average 15min':
            value = int(psutil.getloadavg()[2])
        elif obj.name == 'Ram free':
            value = psutil.virtual_memory().free // B_TO_MB
        elif obj.name == 'Ram shared':
            value = psutil.virtual_memory().shared // B_TO_MB
        elif obj.name == 'Ram buffered':
            value = psutil.virtual_memory().buffers // B_TO_MB
        elif obj.name == 'Ram percent':
            value = psutil.virtual_memory().percent
        elif obj.name == 'Swap free':
            value = psutil.swap_memory().free // B_TO_MB
        elif obj.name == 'Swap percent':
            value = psutil.swap_memory().percent
        elif obj.name == 'Procs':
            value = len(psutil.pids())
        elif obj.name == 'Root partition free':
            value = psutil.disk_usage('/').free // B_TO_MB
        elif obj.name == 'Root partition percent':
            value = psutil.disk_usage('/').percent
        else:
            return

        return value
