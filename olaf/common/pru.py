"""Quick class to control an Octavo A8's PRU"""

from enum import Enum, auto
from os.path import basename, isdir, isfile


class PruState(Enum):
    """All the states a Pru can be in."""

    OFFLINE = auto()
    """PRU is offline"""
    RUNNING = auto()
    """PRU is online and running"""


class PruError(Exception):
    """Raised when a error occurs with a PRU."""


class Pru:
    """
    Handles interterations with a PRU on Octavo A8.

    A PRU is Programible Real-time Unit. It's a microcontroller that shares pins and other
    resources with the core processor.
    """

    def __init__(self, pru_num: int):
        """
        Parameters
        ----------
        pru_num: int
            PRU number. Must be a 0 or 1.

        Raises
        ------
        PruError
            `pru` was not set to 0 or 1 or if the firmware file does not exist.
        """

        if pru_num not in [0, 1]:
            raise PruError(f"pru must be set 0 or 1, not {pru_num}")

        self._pru_num = pru_num

        # remoteproc0 is the power manager M3
        self._pru_dir_path = f"/dev/remoteproc/pruss-core{pru_num}"
        self._pru_state_path = self._pru_dir_path + "/state"
        self._pru_fw_path = self._pru_dir_path + "/firmware"

    def start(self):
        """
        Starts the PRU.

        Raises
        ------
        PruError
            The PRU or PRU firmware was not found.
        """

        if self.state == PruState.RUNNING:
            return  # already running

        self.exists(raise_exception=True)

        with open(self._pru_state_path, "w") as f:
            f.write("start")

    def stop(self):
        """
        Stops the PRU.

        Raises
        ------
        PruError
            The PRU was not found.
        """

        self.exists(raise_exception=True)

        # The state file will throw an errno 22 if a 'stop' command is writen to it while the
        # state is 'offline'
        if self.state == PruState.RUNNING:
            with open(self._pru_state_path, "w") as f:
                f.write("stop")

    def restart(self):
        """Restarts the PRU."""

        self.stop()
        self.start()

    @property
    def state(self) -> PruState:
        """PruState: The state of the PRU."""

        self.exists(raise_exception=True)

        with open(self._pru_state_path, "r") as f:
            state = f.read()[:-1]  # drop the NULL terminator

        return PruState[state.upper()]

    def exists(self, raise_exception: bool = False) -> bool:
        """Check if the PRU exists.

        Parameters
        ----------
        raise_exception: bool
            Raises :py:class:`PruError` if PRU is not found.

        Raises
        ------
        PruError
            Raised when `raise_exception` was set to `True` and the PRU was not found.

        Returns
        -------
        bool
            True if the PRU exists or False if not found.
        """

        ret = isdir(self._pru_dir_path)

        if raise_exception and not ret:
            raise PruError(f"pru{self._pru_num} was not found. is the PRU device tree loaded?")

        return ret

    @property
    def firmware(self) -> str:
        """str: Firmware file name selected. Must be in `/lib/firmware/`."""

        with open(self._pru_fw_path, "r") as f:
            fw_file = f.read()[:-1]  # drop the NULL terminator

        return fw_file

    @firmware.setter
    def firmware(self, fw_path: str):
        if self.state != PruState.OFFLINE:
            raise PruError(f"PRU{self._pru_num} must be in OFFLINE state to set firmware")

        if not (isfile(fw_path) or isfile("/lib/firmware/" + fw_path)):
            raise PruError(f"firmware image {fw_path} not found")

        # path must not include "/lib/firmware/"
        if fw_path.startswith("/lib/firmware/"):
            fw_path = basename(fw_path)

        with open(self._pru_fw_path, "w") as f:
            f.write(fw_path)
