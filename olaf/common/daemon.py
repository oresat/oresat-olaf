'''
A class to control systemd daemons.

While it could use D-Bus, the amount of dependencies needed to work is not worth it.
'''

import subprocess
from enum import Enum


class DaemonState(Enum):
    '''Systemd unit states.'''

    ACTIVE = 0
    RELOADING = 1
    INACTIVE = 2
    FAILED = 3
    ACTIVATING = 4
    DEACTIVATING = 5


class Daemon:
    '''Quick class to control a systemd daemon.'''

    def __init__(self, name: str):
        '''
        Parameters
        ----------
        name: str
            The daemon's systemd service file name; i.e.: ``'mydaemon.service'``.
        '''

        self._name = name

    def start(self):
        '''Start the daemon.'''

        subprocess.run(f'systemctl start {self._name}', shell=True)

    def stop(self):
        '''Stop the daemon.'''

        subprocess.run(f'systemctl stop {self._name}', shell=True)

    def restart(self):
        '''Restart the daemon.'''

        subprocess.run(f'systemctl restart {self._name}', shell=True)

    @property
    def status(self) -> DaemonState:
        '''DaemonState: The state of the daemon.'''

        out = subprocess.run(f'systemctl status {self._name}', capture_output=True, shell=True)
        reply = out.stdout.decode()
        line = reply.split('\n')[2].strip()
        state = line.split(' ')[1]
        return DaemonState[state.upper()]

    @property
    def name(self) -> str:
        '''str: The name of daemon'''

        return self._name
