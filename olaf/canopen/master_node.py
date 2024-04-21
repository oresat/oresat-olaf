"""OreSat CANopen Master Node class to support the C3"""

import logging
from collections import namedtuple
from time import monotonic
from typing import Any, Union

from can import BusABC
from canopen import ObjectDictionary, RemoteNode
from canopen.sdo import SdoArray, SdoRecord, SdoVariable
from canopen.sdo.exceptions import SdoError

from .node import NetworkError, Node, EmcyEvent

logger = logging.getLogger(__file__)

NodeHeartbeatInfo = namedtuple("NodeHeartbeatInfo", ["state", "timestamp", "time_since_boot"])


class EmcyServerHistory:

    def __init__(self, nodes: list[Any]):

        self._data: dict[Any, dict[int, EmcyEvent]] = {node: {} for node in nodes}

    def add(self, node: Any, timestamp: float, code: int, data: bytes):
        """Add a new emcy to the history."""

        if code in self._data[node]:
            self._data[node][code].occurances += 1
            self._data[node][code].last_timestamp = timestamp
            self._data[node][code].data = data
        else:
            self._data[node][code] = EmcyEvent(code, 1, timestamp, data)

    def clear(self):
        """Clear the Emcy history."""

        self._data = {}


class MasterNode(Node):
    """OreSat CANopen Master Node (only used by the C3)"""

    def __init__(
        self,
        od: ObjectDictionary,
        od_db: dict[Any, ObjectDictionary],
        bus: BusABC,
    ):
        """
        Parameters
        ----------
        od: ObjectDictionary
            The CANopen ObjectDictionary
        od_db: dict[Any, ObjectDictionary]
            Database of other nodes's ODs. The dict key will be used by class fields and methods.
        bus: BusABC
            The can bus object to use.
        """

        super().__init__(od, bus)

        self._od_db = od_db

        self._node_id_to_key = {od.node_id: key for key, od in od_db.items()}
        self.emcy_history

        self._remote_nodes = {}
        self.node_status = {}
        for key in od_db:
            if od_db[key] == od:
                continue  # skip itself
            self._remote_nodes[key] = RemoteNode(od_db[key].node_id, od_db[key])
            self.node_status[key] = NodeHeartbeatInfo(
                0xFF,
                0.0,
                0.0,
            )  # 0xFF is a flag, not a CANopen standard

    def _restart_network(self):
        """Restart the CANopen network"""
        super()._restart_network()

        for key, od in self._od_db.items():
            if od == self._od:
                continue  # skip itself
            self.node_status[key] = NodeHeartbeatInfo(0xFF, 0.0, 0.0)
            self._network.subscribe(0x80 + od.node_id, self._on_emergency)
            self._network.subscribe(0x700 + od.node_id, self._on_heartbeat)

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

    def send_sync(self, raise_exception: bool = True):
        """
        Send a CANopen SYNC message.

        Parameters
        ----------
        raise_exception: bool
            Set to False to not raise NetworkError.

        Raises
        ------
        NetworkError
            Cannot send a SYNC message when the network is down.
        """

        if self._network is None:
            if raise_exception:
                raise NetworkError("network is down cannot send an SYNC message")
            return

        try:
            self._network.sync.transmit()
        except Exception:  # pylint: disable=W0718
            pass

    def sdo_get_obj(
        self, key: Any, index: Union[int, str], subindex: Union[int, str, None]
    ) -> [SdoVariable, SdoArray, SdoRecord]:

        if subindex is None:
            return self._remote_nodes[key].sdo[index]
        return self._remote_nodes[key].sdo[index][subindex]

    @property
    def remote_nodes(self) -> dict[Any, RemoteNode]:
        """dict[Any, RemoteNode]: All other node as remote node."""
        return self._remote_nodes

    @property
    def od_db(self) -> dict[Any, ObjectDictionary]:
        """dict[Any, ObjectDictionary]: All other node ODs."""
        return self._od_db

    def sdo_read(
        self, key: Any, index: Union[int, str], subindex: Union[int, str, None]
    ) -> Union[int, str, float, bytes, bool]:
        """
        Read a value from a remote node's object dictionary using an SDO.

        Parameters
        ----------
        key: Any
            The dict key for the node to read from.
        index: int | str
            The index to read from.
        subindex: int | str | None
            The subindex to read from or None.

        Raises
        ------
        NetworkError
            Cannot send a SDO read message when the network is down.
        SdoError
            Error with the SDO.

        Returns
        -------
        int | str | float | bytes | bool
            The value read.
        """

        return self.sdo_get_obj(key, index, subindex).phys

    def sdo_read_bitfield(
        self, key: Any, index: Union[int, str], subindex: Union[int, str, None], field: str
    ) -> int:
        """
        Read an field from a object from another node's OD using a SDO.

        Parameters
        ----------
        key: Any
            The dict key for the node to read from.
        index: int | str
            The index to read from.
        subindex: int | str | None
            The subindex to read from or None.

        Raises
        ------
        NetworkError
            Cannot send a SDO read message when the network is down.
        SdoError
            Error with the SDO.

        Returns
        -------
        int
            The field value.
        """

        obj = self.sdo_get_obj(key, index, subindex)
        bits = obj.od.bit_definitions[field]

        value = 0
        obj_value = obj.phys
        for i in bits:
            tmp = obj_value & (1 << bits[i])
            value |= tmp >> bits[i]
        return value

    def sdo_read_enum(
        self, key: Any, index: Union[int, str], subindex: Union[int, str, None]
    ) -> str:
        """
        Read an enum str from another node's OD using a SDO.

        Parameters
        ----------
        key: Any
            The dict key for the node to read from.
        index: int | str
            The index to read from.
        subindex: int | str | None
            The subindex to read from or None.

        Raises
        ------
        NetworkError
            Cannot send a SDO read message when the network is down.
        SdoError
            Error with the SDO.

        Returns
        -------
        str
            The enum str value.
        """

        obj = self.sdo_get_obj(key, index, subindex)
        obj_value = obj.phys
        return obj.od.value_descriptions[obj_value]

    def sdo_write(
        self,
        key: Any,
        index: Union[int, str],
        subindex: Union[int, str, None],
        value: Union[int, str, float, bytes, bool],
    ):
        """
        Write a value to a remote node's object dictionary using an SDO.

        Parameters
        ----------
        key: Any
            The dict key for the  node to write to.
        index: int | int
            The index to write to.
        subindex: int | str | None
            The subindex to write to or None.
        value: int | str | float | bytes | bool
            The value to write.

        Raises
        ------
        NetworkError
            Cannot send a SDO write message when the network is down.
        SdoError
            Error with the SDO.
        """

        obj = self.sdo_get_obj(key, index, subindex)
        obj.phys = value

    def sdo_write_bitfield(
        self,
        key: Any,
        index: Union[int, str],
        subindex: Union[int, str, None],
        field: str,
        value: int,
    ):
        """
        Write a field from a object to another node's OD using a SDO.

        Parameters
        ----------
        key: Any
            The dict key for the  node to write to.
        index: int | int
            The index to write to.
        subindex: int | str | None
            The subindex to write to or None.
        field: str
            Name of field to write to.
        value: int
            The value to write.

        Raises
        ------
        NetworkError
            Cannot send a SDO write message when the network is down.
        SdoError
            Error with the SDO.
        """

        obj = self.sdo_get_obj(key, index, subindex)

        obj = self.sdo_get_obj(key, index, subindex)
        bits = obj.od.bit_definitions[field]
        offset = min(bits)

        mask = 0
        for i in bits:
            mask |= 1 << bits[i]

        new_value = obj.phys
        new_value ^= mask
        new_value |= value << offset
        obj.phys = new_value

    def sdo_write_enum(
        self, key: Any, index: Union[int, str], subindex: Union[int, str, None], value: str
    ):
        """
        Write a enum str to another node's OD using a SDO.

        Parameters
        ----------
        key: Any
            The dict key for the  node to write to.
        index: int | int
            The index to write to.
        subindex: int | str | None
            The subindex to write to or None.
        value: str
            The enum str value to write.

        Raises
        ------
        NetworkError
            Cannot send a SDO write message when the network is down.
        SdoError
            Error with the SDO.
        """

        obj = self.sdo_get_obj(key, index, subindex)
        tmp = {d: v for v, d in obj.od.value_descriptions}
        obj.phys = tmp[value]
