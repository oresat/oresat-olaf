from time import sleep

import canopen
from oresat_linux_node.apps.os_command import OSCommandState

from . import NodeTestCase


def run_os_command(node: canopen.RemoteNode, command: str):
    '''send os command add give some time to run it'''
    node.sdo[0x1023][0x1].raw = command.encode()
    for i in range(5):
        sleep(0.5)
        if node.sdo[0x1023][0x2].phys != OSCommandState.EXECUTING.value:
            break


class TestOSCommand(NodeTestCase):
    def test_os_command(self):
        self.assertIsNotNone(self.sdo[0x1023][0x1].raw)
        self.assertIn(self.sdo[0x1023][0x2].phys, [e.value for e in OSCommandState])
        self.assertIsNotNone(self.sdo[0x1023][0x3].raw)

        run_os_command(self.oresat_node.node, 'ls')
        self.assertEqual(self.sdo[0x1023][0x2].phys, OSCommandState.NO_ERROR_REPLY)
        self.assertIsNotNone(self.sdo[0x1023][0x3].raw)

        run_os_command(self.oresat_node.node, 'invalid-bash-command')
        self.assertEqual(self.sdo[0x1023][0x2].phys, OSCommandState.ERROR_REPLY)
        self.assertIsNotNone(self.sdo[0x1023][0x3].raw)
