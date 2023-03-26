import canopen
from loguru import logger

from .node import Node


class MasterNode(Node):

    def __init__(self, node: canopen.LocalNode, bus: str):
        '''
        Parameters
        ----------
        node: canopen.LocalNode
            The canopen node obj this class wraps around.
        bus: str
            Which CAN bus to use.
        '''

        super().__init__(node, bus)

        self.node_status = {i: None for i in (2, 0x80)}

    def _restart_network(self):
        '''Restart the CANopen network'''
        super()._restart_network()

        for i in range(0x01, 0x80):
            if i == self._node.object_dictionary.node_id:
                continue  # skip itself
            self._network.subscribe(0x80 + i, self._on_emergency)
            self._network.subscribe(0x700 + i, self._on_heartbeat)

    def _on_heartbeat(self, cob_id: int, data: bytes, timestamp: float):
        '''Callback on node hearbeat messages.'''

        node_id = cob_id - 0x700
        status = int.from_bytes(data, 'little')
        self.node_status[node_id] = (status, timestamp)

    def _on_emergency(self, cob_id: int, data: bytes, timestamp: float):
        '''Callback on node emergency messages.'''

        node_id = cob_id - 0x700
        value_str = data.hex(sep=' ')
        logger.error(f'Node 0x{node_id:02X} raised emergency: {value_str}')
