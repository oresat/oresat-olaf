"""Test the PRU class."""

import unittest
from os.path import isdir

from olaf.board.pru import Pru, PruError, PruState

PRU_EXIST = isdir("/dev/remoteproc/pruss-core0") and isdir("/dev/remoteproc/pruss-core1")


class TestPru(unittest.TestCase):
    """Test the PRU class."""

    @unittest.skipUnless(PRU_EXIST, "requires PRU hardware")
    def test_pru(self):
        """Test the PRU class constructor."""
        pru0 = Pru(0)
        pru0.firmware = "am335x-pru0-fw"
        pru1 = Pru(1)
        pru1.firmware = "/lib/firmware/am335x-pru1-fw"

        # invalid firmware path
        with self.assertRaises(PruError):
            pru1.firmware = "file-that-does-not-exist"
        with self.assertRaises(PruError):
            pru1.firmware = "/lib/firmware/file-that-does-not-exist"

        # invalid pru number
        with self.assertRaises(PruError):
            Pru(2)

        with self.assertRaises(PruError):
            Pru(-1)

    @unittest.skipUnless(PRU_EXIST, "requires PRU hardware")
    def test_pru_control(self):
        """Test the PRU class methods."""

        pru0 = Pru(0)

        self.assertEqual(pru0.state, PruState.OFFLINE)
        pru0.start()
        self.assertEqual(pru0.state, PruState.RUNNING)
        pru0.stop()
        self.assertEqual(pru0.state, PruState.OFFLINE)
        pru0.restart()
        self.assertEqual(pru0.state, PruState.RUNNING)
        pru0.stop()
        self.assertEqual(pru0.state, PruState.OFFLINE)
