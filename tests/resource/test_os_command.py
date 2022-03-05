import unittest
from time import sleep

import canopen
from olaf.resources.os_command import OSCommandState, OSCommandResource

from . import TestApp


def run_os_command(node: canopen.LocalNode, command: str):
    '''send os command add give some time to run it'''
    node.sdo[0x1023][0x1].raw = command.encode()
    for i in range(5):
        sleep(0.5)
        if node.sdo[0x1023][0x2].phys != OSCommandState.EXECUTING.value:
            break


class TestOSCommand(unittest.TestCase):
    def setUp(self):
        self.app = TestApp()
        self.node = self.app.node
        self.app.add_resource(OSCommandResource(self.node))
        self.app.start()

    def tearDown(self):
        self.app.stop()

    def test_os_command(self):

        self.assertIsNotNone(self.node.sdo[0x1023][0x1].raw)
        self.assertIn(self.node.sdo[0x1023][0x2].phys, [e.value for e in OSCommandState])
        self.assertIsNotNone(self.node.sdo[0x1023][0x3].raw)

        run_os_command(self.node, 'ls')
        self.assertEqual(self.node.sdo[0x1023][0x2].phys, OSCommandState.NO_ERROR_REPLY)
        self.assertIsNotNone(self.node.sdo[0x1023][0x3].raw)

        run_os_command(self.node, 'invalid-bash-command')
        self.assertEqual(self.node.sdo[0x1023][0x2].phys, OSCommandState.ERROR_REPLY)
        self.assertIsNotNone(self.node.sdo[0x1023][0x3].raw)
