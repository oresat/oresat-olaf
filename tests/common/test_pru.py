import unittest
from os.path import isdir

from olaf.common.pru import PRU, PRUState, PRUError


PRU_EXIST = isdir('/dev/remoteproc/pruss-core0') and isdir('/dev/remoteproc/pruss-core1')


class TestPRU(unittest.TestCase):

    @unittest.skipUnless(PRU_EXIST, 'requires PRU hardware')
    def test_pru(self):
        PRU(0, 'am335x-pru0-fw')
        PRU(1, '/lib/firmware/am335x-pru1-fw')

        # invalid firmware path
        with self.assertRaises(PRUError):
            PRU(1, 'file-that-does-not-exist')
        with self.assertRaises(PRUError):
            PRU(1, '/lib/firmware/file-that-does-not-exist')

        # invalid pru number
        with self.assertRaises(PRUError):
            PRU(2, 'am335x-pru1-fw')

        with self.assertRaises(PRUError):
            PRU(-1, 'am335x-pru1-fw')

    @unittest.skipUnless(PRU_EXIST, 'requires PRU hardware')
    def test_pru_control(self):
        pru0 = PRU(0, 'am335x-pru0-fw')

        self.assertEqual(pru0.state, PRUState.OFFLINE)

        pru0.start()

        self.assertEqual(pru0.state, PRUState.RUNNING)

        pru0.stop()

        pru0.restart()

        self.assertEqual(pru0.state, PRUState.RUNNING)

        pru0.stop()

        self.assertEqual(pru0.state, PRUState.OFFLINE)
