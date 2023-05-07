from time import time

import canopen
from loguru import logger

from .node import Node, NetworkError


class MasterNode(Node):
    '''OreSat CANopen Master Node'''

    def __init__(self, od: canopen.ObjectDictionary, bus: str):
        '''
        Parameters
        ----------
        od: canopen.ObjectDictionary
            The CANopen ObjectDictionary
        bus: str
            Which CAN bus to use.
        '''

        super().__init__(od, bus)

        self.node_status = {}
        for i in range(0x01, 0x80):
            if i == self._od.node_id:
                continue  # skip itself
            self.node_status[i] = (0xFF, time())  # 0xFF is a flag, not a CANopen standard

    def _restart_network(self):
        '''Restart the CANopen network'''
        super()._restart_network()

        for i in range(0x01, 0x80):
            if i == self._od.node_id:
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

    def send_sync(self):
        '''
        Send a CANopen SYNC message.

        Raises
        ------
        NetworkError
            Cannot send a SYNC message when the network is down.
        '''

        if self._network is None:
            raise NetworkError('network is down cannot send an SYNC message')

        self._network.sync.transmit()

    def sdo_read(self, node_id: int, index: int, subindex: int) -> bytes:
        '''
        Read a value from a remote node's object dictionary using an SDO.

        Parameters
        ----------
        node_id: int
            The id of the node to read from.
        index: int
            The index to read from.
        subindex: int
            The subindex to read from.

        Raises
        ------
        NetworkError
            Cannot send a SDO read message when the network is down.
        canopen.SdoError
            Error with the SDO.

        Returns
        -------
        bytes
            The raw value read.
        '''

        if self._network is None:
            raise NetworkError('network is down cannot send an SDO read message')

        if node_id in self._network:
            node = self._network[node_id]
        else:
            node = canopen.RemoteNode(node_id, canopen.ObjectDictionary())
            self._network.add_node(node)

        return node.sdo.upload(index, subindex)

    def sdo_write(self, node_id: int, index: int, subindex: int, value: bytes):
        '''
        Write a value to a remote node's object dictionary using an SDO.

        Parameters
        ----------
        node_id: int
            The id of the node to write to.
        index: int
            The index to write to.
        subindex: int
            The subindex to write to.
        value: bytes
            The raw value to write.

        Raises
        ------
        NetworkError
            Cannot send a SDO write message when the network is down.
        canopen.SdoError
            Error with the SDO.
        '''

        if self._network is None:
            raise NetworkError('network is down cannot send an SDO write message')

        if node_id in self._network:
            node = self._network[node_id]
        else:
            node = canopen.RemoteNode(node_id, canopen.ObjectDictionary())
            self._network.add_node(node)

        node.sdo.download(index, subindex, value)
