
import canopen

BUS = 'vcan0'
EDS_FILE = 'oresat_linux_node.eds'
NODE_ID = 0x10


def oresat_node():
    network = canopen.Network()
    network.connect(bustype='socketcan', channel=BUS)
    node = canopen.RemoteNode(NODE_ID, EDS_FILE)
    network.add_node(node)

    return node
