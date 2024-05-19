"""OreSat CANopen Master Node class to support the C3"""

from collections import namedtuple
from time import monotonic
from typing import Any, Dict, Union

import canopen
from canopen.sdo import SdoArray, SdoRecord, SdoVariable
from loguru import logger

from ..canopen.network import CanNetwork
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

    @property
    def remote_nodes(self) -> dict[Any, canopen.RemoteNode]:
        """dict[Any, canopen.RemoteNode]: All other node as remote node."""
        return self._remote_nodes

    @property
    def od_db(self) -> dict[Any, canopen.ObjectDictionary]:
        """dict[Any, canopen.ObjectDictionary]: All other node ODs."""
        return self._od_db

    def _sdo_get_obj(
        self, key: Any, index: Union[int, str], subindex: Union[int, str, None]
    ) -> [SdoVariable, SdoArray, SdoRecord]:

        if subindex is None:
            return self._remote_nodes[key].sdo[index]
        return self._remote_nodes[key].sdo[index][subindex]

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
        canopen.sdo.exceptions.SdoError
            Error with the SDO.

        Returns
        -------
        int | str | float | bytes | bool
            The value read.
        """

        return self._sdo_get_obj(key, index, subindex).phys

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
        canopen.sdo.exceptions.SdoError
            Error with the SDO.

        Returns
        -------
        int
            The field value.
        """

        obj = self._sdo_get_obj(key, index, subindex)
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
        canopen.sdo.exceptions.SdoError
            Error with the SDO.

        Returns
        -------
        str
            The enum str value.
        """

        obj = self._sdo_get_obj(key, index, subindex)
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
        canopen.sdo.exceptions.SdoError
            Error with the SDO.
        """

        obj = self._sdo_get_obj(key, index, subindex)
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
            Cannot send a SDO read message when the network is down.
        canopen.sdo.exceptions.SdoError
            Error with the SDO.
        """

        obj = self._sdo_get_obj(key, index, subindex)
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
            Cannot send a SDO read message when the network is down.
        canopen.sdo.exceptions.SdoError
            Error with the SDO.
        """

        obj = self._sdo_get_obj(key, index, subindex)
        tmp = {d: v for v, d in obj.od.value_descriptions}
        obj.phys = tmp[value]

    def send_rpdo(self, rpdo: int, raise_error: bool = True):
        """
        Send a RPDO. Will not be sent if not node is not in operational state.

        Parameters
        ----------
        rpdo: int
            RPDO number to send, should be between 1 and 16.
        raise_error: bool
            Set to False to not raise NetworkError.

        Raises
        ------
        ValueError
            Invalud rpdo value.
        NetworkError
            Cannot send a RPDO read message when the network is down.
        """

        if rpdo < 1:
            raise ValueError("RPDO number must be greater than 1")

        rpdo -= 1  # number to offset
        comm_index = 0x1400 + rpdo
        map_index = 0x1600 + rpdo
        self._send_pdo(comm_index, map_index, raise_error)
