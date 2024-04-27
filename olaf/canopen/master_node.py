"""OreSat CANopen Master Node class to support the C3"""

from collections import namedtuple
from time import monotonic
from typing import Any, Dict, Union

import canopen
from loguru import logger

from ..canopen.network import CanNetwork, CanNetworkError, CanNetworkState
from .node import Node

NodeHeartbeatInfo = namedtuple("NodeHeartbeatInfo", ["state", "timestamp", "time_since_boot"])


class MasterNode(Node):
    """OreSat CANopen Master Node (only used by the C3)"""

    def __init__(
        self,
        network: CanNetwork,
        od: canopen.ObjectDictionary,
        od_db: Dict[Any, canopen.ObjectDictionary],
    ):
        """
        Parameters
        ----------
        network: CanNetwork
            The CAN network
        od: canopen.ObjectDictionary
            The CANopen ObjectDictionary
        od_db: Dict[Any, canopen.ObjectDictionary]
            Database of other nodes's ODs. The dict key will be used by class fields and methods.
        """

        super().__init__(network, od)

        self._od_db = od_db
        self.network = network
        self._node_id_to_key = {od.node_id: key for key, od in od_db.items()}

        self._remote_nodes = {}
        self.node_status = {}
        for k, v in self._od_db.items():
            if v == od:
                continue  # skip itself
            self._remote_nodes[k] = canopen.RemoteNode(v.node_id, v)
            self.node_status[k] = NodeHeartbeatInfo(
                0xFF,
                0.0,
                0.0,
            )  # 0xFF is a flag, not a CANopen standard
            self._network.subscribe(0x80 + v.node_id, self._on_emergency)
            self._network.subscribe(0x700 + v.node_id, self._on_heartbeat)

        self._network.add_reset_callback(self._restart_network)

    def _restart_network(self):
        """Restart the CANopen network"""

        for key, od in self._od_db.items():
            if od == self._od:
                continue  # skip itself
            self.node_status[key] = NodeHeartbeatInfo(0xFF, 0.0, 0.0)

        for remote_node in self._remote_nodes.values():
            self._network.add_node(remote_node)

    def _on_heartbeat(self, cob_id: int, data: bytes, timestamp: float):
        """Callback on node hearbeat messages."""

        node_id = cob_id - 0x700
        status = int.from_bytes(data, "little")
        key = self._node_id_to_key[node_id]
        self.node_status[key] = NodeHeartbeatInfo(status, timestamp, monotonic())

    def _on_emergency(self, cob_id: int, data: bytes, timestamp: float):  # pylint: disable=W0613
        """Callback on node emergency messages."""

        node_id = cob_id - 0x80
        value_str = data.hex(sep=" ")
        logger.error(f"node {node_id:02X} raised emergency: {value_str}")

    def send_sync(self):
        """
        Send a CANopen SYNC message.
        """

        self._network.send_message(0x80, b"", False)

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
        CanNetworkError
            Cannot send a SDO read message when the network is down.
        canopen.SdoError
            Error with the SDO.

        Returns
        -------
        Any
            The value read.
        """

        if self._network.status == CanNetworkState.NETWORK_UP:
            raise CanNetworkError("network is down cannot send an SDO read message")

        if subindex == 0 and isinstance(self._od_db[key][index], canopen.objectdictionary.Variable):
            value = self._remote_nodes[key].sdo[index].raw
        else:
            value = self._remote_nodes[key].sdo[index][subindex].raw

        return value

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
        CanNetworkError
            Cannot send a SDO write message when the network is down.
        canopen.SdoError
            Error with the SDO.
        """

        if self._network.status == CanNetworkState.NETWORK_UP:
            raise CanNetworkError("network is down cannot send an SDO write message")

        if subindex == 0 and isinstance(self._od_db[key][index], canopen.objectdictionary.Variable):
            self._remote_nodes[key].sdo[index].raw = value
        else:
            self._remote_nodes[key].sdo[index][subindex].raw = value

    @property
    def remote_nodes(self) -> dict[Any, canopen.RemoteNode]:
        """dict[Any, canopen.RemoteNode]: All other node as remote node."""
        return self._remote_nodes

    @property
    def od_db(self) -> dict[Any, canopen.ObjectDictionary]:
        """dict[Any, canopen.ObjectDictionary]: All other node ODs."""
        return self._od_db
