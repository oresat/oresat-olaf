
from os.path import exists, isdir
from enum import Enum, auto


class PRUState(Enum):
    '''All the states a PRU can be in.'''

    OFFLINE = auto()
    '''PRU is offline'''

    RUNNING = auto()
    '''PRU is online and running'''


class PRUError(Exception):
    '''Raised when a error occurs with a PRU.'''


class PRU:
    '''Handles interterations with a PRU on Octavo A8.

    A PRU is Programible Real-time Units). It's a microcontroller that shares pins and other
    resources with the core processor.
    '''

    def __init__(self, pru: int, fw_path: str):
        '''
        Parameters
        ----------
        pru: int
            PRU number. Must be a 0 or 1.
        fw_path: str
            Absolute file path to firmware. Firmware file must be in `/lib/firmware/`.

        Raises
        ------
        PRUError
            `pru` was not set to 0 or 1.
        '''

        if pru not in [0, 1]:
            PRUError('pru must be set 0 or 1')

        self._pru = pru
        self._fw_path = fw_path
        if not self._fw_path.startswith('/lib/firmware/'):
            self._fw_path = '/lib/firmware/' + self._fw

        # remoteproc0 is the power manager M3
        self._rproc_dir_path = '/sys/class/remoteproc/remoteproc' + str(pru + 1)
        self._rproc_state_path = self._rproc_dir_path + '/state'

    def start(self):
        '''Starts the PRU.

        Raises
        ------
        PRUError
            The PRU or PRU firmware was not found.
        '''

        self.exists(raise_exception=True)

        if not exists(self._fw_path):
            raise PRUError(f'firmware file {self.fw_path} does not exist')

        with open(self._pru_fw_path, 'w') as fptr:
            fptr.write(self._fw_path)

        if self.state() == PRUState.OFFLINE:
            with open(self._pru_state_path, 'w') as fptr:
                fptr.write('start')

    def stop(self):
        '''Stops the PRU.

        Raises
        ------
        PRUError
            The PRU was not found.
        '''

        self.exists(raise_exception=True)

        # The state file will throw an errno 22 if a 'stop' command is writen to it while the
        # state is 'offline'
        if self.state() == PRUState.RUNNING:
            with open(self._pru_state_path, 'w') as fptr:
                fptr.write('stop')

    def restart(self):
        '''Restarts the PRU.'''

        self.stop()
        self.start()

    def state(self) -> PRUState:
        '''Get the state of the PRU.

        Raises
        ------
        PRUError
            The PRU was not found.

        Returns
        -------
        PRUState
            The PRU state
        '''

        self.exists(raise_exception=True)

        with open(self._pru_state_path, 'r') as f:
            state = f.read()[:-1]  # drop the NULL terminator

        return PRUState[state.upper()]

    def exists(self, raise_exception: bool = False) -> bool:
        '''Check if the PRU exists.

        Parameters
        ----------
        raise_exception: bool
            Raises :py:class:`PRUError` if PRU is not found.

        Raises
        ------
        PRUError
            Raised when `raise_exception` was set to `True` and the PRU was not found.

        Returns
        -------
        bool
            True if the PRU exists or False if not found.
        '''

        ret = isdir(self._rproc_dir_path)

        if raise_exception and not ret:
            raise PRUError(f'pru{self._pru} was not found. is the PRU device tree loaded?')

        return ret
