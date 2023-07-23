import unittest
from os.path import isdir

from olaf.common.pru import Pru, PruState, PruError

PRU_EXIST = isdir('/dev/remoteproc/pruss-core0') and isdir('/dev/remoteproc/pruss-core1')


class TestPRU(unittest.TestCase):

    @unittest.skipUnless(PRU_EXIST, 'requires PRU hardware')
    def test_pru(self):
        pru0 = Pru(0)
        pru0.firmware = 'am335x-pru0-fw'
        pru1 = Pru(1)
        pru1.firmware = '/lib/firmware/am335x-pru1-fw'

        # invalid firmware path
        with self.assertRaises(PruError):
            pru1.firmware = 'file-that-does-not-exist'
        with self.assertRaises(PruError):
            pru1.firmware = '/lib/firmware/file-that-does-not-exist'

        # invalid pru number
        with self.assertRaises(PruError):
            Pru(2)

        with self.assertRaises(PruError):
            Pru(-1)

    @unittest.skipUnless(PRU_EXIST, 'requires PRU hardware')
    def test_pru_control(self):
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
