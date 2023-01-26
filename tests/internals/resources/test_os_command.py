import unittest
from time import sleep

import canopen
from olaf._internals.resources.os_command import OSCommandState, OSCommandResource

from . import MockApp

INDEX = 0x1023


def run_os_command(node: canopen.LocalNode, command: str):
    '''send os command add give some time to run it'''
    node.sdo[INDEX][0x1].raw = command.encode()
    for i in range(5):
        sleep(1)
        if node.sdo[INDEX][0x2].phys != OSCommandState.EXECUTING.value:
            break


class TestOSCommand(unittest.TestCase):
    def setUp(self):
        self.app = MockApp()
        self.node = self.app.node
        self.app.add_resource(OSCommandResource)
        self.app.start()

    def tearDown(self):
        self.app.stop()

    def test_os_command(self):

        self.assertIsNotNone(self.node.sdo[INDEX][0x1].raw)
        self.assertIn(self.node.sdo[INDEX][0x2].phys, [e.value for e in OSCommandState])
        self.assertIsNotNone(self.node.sdo[INDEX][0x3].raw)

        run_os_command(self.node, 'ls')
        self.assertEqual(self.node.sdo[INDEX][0x2].phys, OSCommandState.NO_ERROR_REPLY)
        self.assertIsNotNone(self.node.sdo[INDEX][0x3].raw)

        run_os_command(self.node, 'invalid-bash-command')
        # self.assertEqual(self.node.sdo[INDEX][0x2].phys, OSCommandState.ERROR_REPLY)
        # self.assertIsNotNone(self.node.sdo[INDEX][0x3].raw)
