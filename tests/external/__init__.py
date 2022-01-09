import unittest
from threading import Thread
from loguru import logger

import canopen
from oresat_linux_node import OreSatNode

BUS = 'vcan0'
EDS_FILE = 'oresat_linux_node.eds'
NODE_ID = 0x10


def oresat_node():
    network = canopen.Network()
    network.connect(bustype='socketcan', channel=BUS)
    node = canopen.RemoteNode(NODE_ID, EDS_FILE)
    network.add_node(node)

    return node


class NodeTestCase(unittest.TestCase):
    def setUp(self):
        self.oresat_node = OreSatNode('oresat_linux_node.eds', 'vcan0', 0x10)
        logger.disable('oresat_linux_node')
        self.thread = Thread(target=self.oresat_node.run)
        self.thread.start()
        self.sdo = self.oresat_node.node.sdo

    def tearDown(self):
        self.oresat_node.stop()
        self.thread.join()
