'''OreSat CANopen Master Node class to support the C3'''

from time import time
from typing import Any

import canopen
from loguru import logger
from oresat_configs import NodeId

from .node import Node, NetworkError


class MasterNode(Node):
    '''OreSat CANopen Master Node (only used by the C3)'''

    def __init__(self, od: canopen.ObjectDictionary, bus: str, od_db: dict):
        '''
        Parameters
        ----------
        od: canopen.ObjectDictionary
            The CANopen ObjectDictionary
        bus: str
            Which CAN bus to use.
        od_db: dict
            Database of other nodes's ODs.
        '''

        super().__init__(od, bus)

        self._od_db = od_db

        self._remote_nodes = {}
        self.node_status = {}
        for node_id in od_db:
            if node_id == self._od.node_id:
                continue  # skip itself
            self._remote_nodes[node_id] = canopen.RemoteNode(node_id.value, od_db[node_id])
            self.node_status[node_id] = (0xFF, time())  # 0xFF is a flag, not a CANopen standard

    def _restart_network(self):
        '''Restart the CANopen network'''
        super()._restart_network()

        for node_id in self._od_db:
            if node_id == self._od.node_id:
                continue  # skip itself
            self._network.subscribe(0x80 + node_id, self._on_emergency)
            self._network.subscribe(0x700 + node_id, self._on_heartbeat)

    def _on_heartbeat(self, cob_id: int, data: bytes, timestamp: float):
        '''Callback on node hearbeat messages.'''

        node_id = cob_id - 0x700
        status = int.from_bytes(data, 'little')
        self.node_status[NodeId(node_id)] = (status, timestamp)

    def _on_emergency(self, cob_id: int, data: bytes, timestamp: float):
        '''Callback on node emergency messages.'''

        node_id = cob_id - 0x700
        value_str = data.hex(sep=' ')
        logger.error(f'{NodeId(node_id).name} raised emergency: {value_str}')

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

    def sdo_read(self, node_id: NodeId, index: int or str, subindex: int or str) -> Any:
        '''
        Read a value from a remote node's object dictionary using an SDO.

        Parameters
        ----------
        node_id: NodeId
            The id of the node to read from.
        index: int or str
            The index to read from.
        subindex: int or str
            The subindex to read from.

        Raises
        ------
        NetworkError
            Cannot send a SDO read message when the network is down.
        canopen.SdoError
            Error with the SDO.

        Returns
        -------
        Any
            The value read.
        '''

        if self._network is None:
            raise NetworkError('network is down cannot send an SDO read message')

        return self._remote_nodes[node_id].sdo[index][subindex].phys

    def sdo_write(self, node_id: NodeId, index: int, subindex: int, value: Any):
        '''
        Write a value to a remote node's object dictionary using an SDO.

        Parameters
        ----------
        node_id: NodeId
            The id of the node to write to.
        index: int
            The index to write to.
        subindex: int
            The subindex to write to.
        value: Any
            The value to write.

        Raises
        ------
        NetworkError
            Cannot send a SDO write message when the network is down.
        canopen.SdoError
            Error with the SDO.
        '''

        if self._network is None:
            raise NetworkError('network is down cannot send an SDO write message')

        self._remote_nodes[node_id].sdo[index][subindex].phys = value
