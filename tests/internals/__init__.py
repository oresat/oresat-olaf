from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from pathlib import Path

import canopen
from canopen.objectdictionary import ODVariable
from canopen.sdo import SdoVariable
from oresat_configs import OreSatConfig

from olaf import OreSatFileCache, Resource, Service
from olaf.canopen.network import CanNetwork
from olaf.canopen.node import Node


class MockNode(Node):
    def __init__(self, cachedir: Path) -> None:
        od = OreSatConfig().od_db["gps"]
        network = CanNetwork("virtual", "vcan0")
        super().__init__(network, od)

        self._fread_cache = OreSatFileCache(cachedir / "fread")
        self._fread_cache.clear()
        self._fwrite_cache = OreSatFileCache(cachedir / "fwrite")
        self._fwrite_cache.clear()

        self._setup_node()

    def send_tpdo(self, tpdo: int, raise_error: bool = True) -> None:  # noqa: FBT001,FBT002
        pass  # override to do nothing


class MockApp:
    '''Testing app that manages a single Resource or Service.'''

    def __init__(self, cachedir: Path, resource: Resource | Service) -> None:
        super().__init__()

        self.node = MockNode(cachedir)
        self.resource = resource

    def sdo_read(self, index: int | str, subindex: None | int | str) -> int | float | str | bytes:
        co_node = self.node._node
        domain = canopen.objectdictionary.DOMAIN

        obj = co_node.object_dictionary[index]
        sdo = co_node.sdo[index]
        if subindex is None:
            assert isinstance(obj, ODVariable)
            assert isinstance(sdo, SdoVariable)
            if obj.data_type == domain:
                return sdo.raw
            return sdo.phys
        assert not isinstance(obj, ODVariable)
        assert not isinstance(sdo, SdoVariable)
        if obj[subindex].data_type == domain:
            return sdo[subindex].raw
        return sdo[subindex].phys

    def sdo_write(
        self,
        index: int | str,
        subindex: None | int | str,
        value: bool | str | bytes,  # noqa: FBT001
    ) -> None:
        co_node = self.node._node
        domain = canopen.objectdictionary.DOMAIN

        obj = co_node.object_dictionary[index]
        sdo = co_node.sdo[index]
        if subindex is None:
            assert isinstance(obj, ODVariable)
            assert isinstance(sdo, SdoVariable)
            if obj.data_type == domain:
                sdo.raw = value
            else:
                sdo.phys = value
        else:
            assert not isinstance(obj, ODVariable)
            assert not isinstance(sdo, SdoVariable)
            if obj[subindex].data_type == domain:
                sdo[subindex].raw = value
            else:
                sdo[subindex].phys = value

    def start(self) -> None:
        self.resource.start(self.node)

    def stop(self) -> None:
        if isinstance(self.resource, Resource):
            self.resource.end()
        else:
            self.resource.stop()
        self.node._destroy_node()
        self.node.stop()
