"""OreSat CANopen Master Node class to support the C3"""

from collections import namedtuple
from typing import Any, Dict, Union

import canopen
from loguru import logger

from .node import NetworkError, Node

NodeHeartbeatInfo = namedtuple("NodeHeartbeatInfo", ["state", "timestamp"])


class MasterNode(Node):
    """OreSat CANopen Master Node (only used by the C3)"""

    def __init__(
        self, od: canopen.ObjectDictionary, bus: str, od_db: Dict[Any, canopen.ObjectDictionary]
    ):
        """
        Parameters
        ----------
        od: canopen.ObjectDictionary
            The CANopen ObjectDictionary
        bus: str
            Which CAN bus to use.
        od_db: Dict[Any, canopen.ObjectDictionary]
            Database of other nodes's ODs. The dict key will be used by class fields and methods.
        """

        super().__init__(od, bus)

        self._od_db = od_db

        self._node_id_to_key = {od.node_id: key for key, od in od_db.items()}

        self._remote_nodes = {}
        self.node_status = {}
        for key in od_db:
            if od_db[key] == od:
                continue  # skip itself
            self._remote_nodes[key] = canopen.RemoteNode(od_db[key].node_id, od_db[key])
            self.node_status[key] = NodeHeartbeatInfo(
                0xFF, 0.0
            )  # 0xFF is a flag, not a CANopen standard

    def _restart_network(self):
        """Restart the CANopen network"""
        super()._restart_network()

        for key, od in self._od_db.items():
            if od == self._od:
                continue  # skip itself
            self.node_status[key] = NodeHeartbeatInfo(0xFF, 0.0)
            self._network.subscribe(0x80 + od.node_id, self._on_emergency)
            self._network.subscribe(0x700 + od.node_id, self._on_heartbeat)

        for remote_node in self._remote_nodes.values():
            self._network.add_node(remote_node)

    def _on_heartbeat(self, cob_id: int, data: bytes, timestamp: float):
        """Callback on node hearbeat messages."""

        node_id = cob_id - 0x700
        status = int.from_bytes(data, "little")
        key = self._node_id_to_key[node_id]
        self.node_status[key] = NodeHeartbeatInfo(status, timestamp)

    def _on_emergency(self, cob_id: int, data: bytes, timestamp: float):  # pylint: disable=W0613
        """Callback on node emergency messages."""

        node_id = cob_id - 0x80
        value_str = data.hex(sep=" ")
        logger.error(f"node {node_id:02X} raised emergency: {value_str}")

    def send_sync(self):
        """
        Send a CANopen SYNC message.

        Raises
        ------
        NetworkError
            Cannot send a SYNC message when the network is down.
        """

        if self._network is None:
            raise NetworkError("network is down cannot send an SYNC message")

        self._network.sync.transmit()

    def sdo_read(self, key: Any, index: Union[int, str], subindex: Union[int, str]) -> Any:
        """
        Read a value from a remote node's object dictionary using an SDO.

        Parameters
        ----------
        key: Any
            The dict key for the node to read from.
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
        """

        if self._network is None:
            raise NetworkError("network is down cannot send an SDO read message")

        return self._remote_nodes[key].sdo[index][subindex].phys

    def sdo_write(self, key: Any, index: int, subindex: int, value: Any):
        """
        Write a value to a remote node's object dictionary using an SDO.

        Parameters
        ----------
        key: Any
            The dict key for the  node to write to.
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
        """

        if self._network is None:
            raise NetworkError("network is down cannot send an SDO write message")

        self._remote_nodes[key].sdo[index][subindex].phys = value
