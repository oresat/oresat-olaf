'''A quick wrapper class to control systemd daemons using D-Bus.'''

from enum import Enum

from pydbus import SystemBus


class DaemonState(Enum):
    '''Systemd unit states.'''

    ACTIVE = 0
    RELOADING = 1
    INACTIVE = 2
    FAILED = 3
    ACTIVATING = 4
    DEACTIVATING = 5


class Daemon:
    '''Very small wrapper ontop of pydbus to abstract away D-Bus to control systemd daemons.'''

    # only need on instance of these for all instances of Daemon
    _bus = SystemBus()
    _systemd = _bus.get('.systemd1')

    def __init__(self, name: str):
        '''
        Parameters
        ----------
        name: str
            The daemon's systemd service file name; i.e.: ``'mydaemon.service'``.
        '''

        self._name = name
        unit_path = self._systemd.GetUnit(self._name)
        self._unit = self._bus.get('.systemd1', unit_path)

    def start(self):
        '''Start the daemon.'''

        self._unit.Start(self._name, 'fail')

    def stop(self):
        '''Stop the daemon.'''

        self._unit.Stop(self._name, 'fail')

    def restart(self):
        '''Restart the daemon.'''

        self._unit.Restart(self._name, 'fail')

    @property
    def status(self) -> DaemonState:
        '''DaemonState: The state of the daemon.'''

        return DaemonState[self._unit.ActiveState.upper()]

    @property
    def name(self) -> str:
        '''str: The name of daemon'''

        return self._name
