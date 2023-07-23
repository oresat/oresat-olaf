import unittest
from time import sleep

from olaf._internals.services.os_command import OSCommandState, OSCommandService

from . import MockApp


class TestOSCommand(unittest.TestCase):

    def setUp(self):

        self.app = MockApp()
        self.app.add_service(OSCommandService())
        self.app.start()
        self.index = self.app.service.index

    def tearDown(self):

        self.app.stop()

    def run_os_command(self, command: str):
        '''send os command add give some time to run it'''

        self.app.sdo_write(self.index, 0x1, command)
        for i in range(50):
            sleep(0.1)
            value = self.app.sdo_read(self.index, 0x2)
            if value != OSCommandState.EXECUTING.value:
                break

    def test_os_command(self):

        self.assertIsNotNone(self.app.sdo_read(self.index, 0x1))
        self.assertIn(self.app.sdo_read(self.index, 0x2), [e.value for e in OSCommandState])
        self.assertIsNotNone(self.app.sdo_read(self.index, 0x3))

        self.run_os_command('ls'.encode())
        self.assertEqual(self.app.sdo_read(self.index, 0x2), OSCommandState.NO_ERROR_REPLY)
        self.assertIsNotNone(self.app.sdo_read(self.index, 0x3))

        self.run_os_command('invalid-bash-command'.encode())
        self.assertEqual(self.app.sdo_read(self.index, 0x2), OSCommandState.ERROR_REPLY)
        self.assertIsNotNone(self.app.sdo_read(self.index, 0x3))
