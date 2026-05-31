"""Test the PRU class."""

from pathlib import Path

import pytest

from olaf.board.pru import Pru, PruError, PruState

PRU0 = Path("/dev/remoteproc/pruss-core0").is_dir()
PRU1 = Path("/dev/remoteproc/pruss-core1").is_dir()


class TestPru:
    @pytest.mark.skipif(not (PRU0 and PRU1), reason="requires PRU hardware")
    def test_pru(self) -> None:
        """Test the PRU class constructor."""
        pru0 = Pru(0)
        pru0.firmware = "am335x-pru0-fw"
        pru1 = Pru(1)
        pru1.firmware = "/lib/firmware/am335x-pru1-fw"

        # invalid firmware path
        with pytest.raises(PruError):
            pru1.firmware = "file-that-does-not-exist"
        with pytest.raises(PruError):
            pru1.firmware = "/lib/firmware/file-that-does-not-exist"

    def test_pru_invalid(self) -> None:
        # invalid pru number
        with pytest.raises(PruError):
            Pru(2)
        with pytest.raises(PruError):
            Pru(-1)

    @pytest.mark.skipif(not PRU0, reason="requires PRU hardware")
    def test_pru_control(self) -> None:
        """Test the PRU class methods."""
        pru0 = Pru(0)
        assert pru0.state == PruState.OFFLINE
        pru0.start()
        assert pru0.state == PruState.RUNNING
        pru0.stop()
        assert pru0.state == PruState.OFFLINE
        pru0.restart()
        assert pru0.state == PruState.RUNNING
        pru0.stop()
        assert pru0.state == PruState.OFFLINE
