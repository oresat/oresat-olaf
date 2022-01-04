from time import sleep

import canopen
from oresat_linux_node.apps.os_command import OSCommandState

from . import oresat_node


def run_os_command(node: canopen.RemoteNode, command: str):
    '''send os command add give some time to run it'''
    node.sdo[0x1023][0x1].raw = command.encode()
    for i in range(5):
        sleep(0.5)
        if node.sdo[0x1023][0x2].phys != OSCommandState.EXECUTING.value:
            break


def test_os_command_permissions():
    node = oresat_node()

    assert node.sdo[0x1023][0x1].raw
    assert node.sdo[0x1023][0x2].phys in [e.value for e in OSCommandState]
    assert node.sdo[0x1023][0x3].raw

    run_os_command(node, 'ls')
    assert node.sdo[0x1023][0x2].phys == OSCommandState.NO_ERROR_REPLY.value
    assert node.sdo[0x1023][0x3].raw

    run_os_command(node, 'invalid-bash-command')
    assert node.sdo[0x1023][0x2].phys == OSCommandState.ERROR_REPLY.value
    assert node.sdo[0x1023][0x3].raw

    node.network.disconnect()
