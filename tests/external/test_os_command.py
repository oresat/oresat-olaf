import unittest
from time import sleep

import canopen
from oresat_linux_node.apps.os_command import OSCommandState, OSCommandApp

from . import TestNode


def run_os_command(node: canopen.LocalNode, command: str):
    '''send os command add give some time to run it'''
    node.sdo[0x1023][0x1].raw = command.encode()
    for i in range(5):
        sleep(0.5)
        if node.sdo[0x1023][0x2].phys != OSCommandState.EXECUTING.value:
            break


class TestOSCommand(unittest.TestCase):
    def setUp(self):
        self.oresat = TestNode()
        self.node = self.oresat.node
        self.oresat.add_app(OSCommandApp(self.node))
        self.oresat.start()

    def tearDown(self):
        self.oresat.stop()

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
