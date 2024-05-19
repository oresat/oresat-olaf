"""Mock node for testing services."""

import canopen
from oresat_configs import OreSatConfig, OreSatId

from olaf import OreSatFileCache, Service, logger
from olaf.canopen.network import CanNetwork
from olaf.canopen.node import Node

logger.disable("olaf")


class MockNode(Node):
    """Mock node for testing services."""

    def __init__(self):
        od = OreSatConfig(OreSatId.ORESAT0).od_db["gps"]
        network = CanNetwork("virtual", "vcan0")
        super().__init__(network, od)

        self._fread_cache = OreSatFileCache("/tmp/fread")
        self._fread_cache.clear()
        self._fwrite_cache = OreSatFileCache("/tmp/fwrite")
        self._fwrite_cache.clear()

        self._setup_node()

    def send_tpdo(self, tpdo: int, raise_error: bool = True):
        pass  # override to do nothing


class MockApp:
    """Mock app for testing services."""

    def __init__(self):
        super().__init__()

        self.node = MockNode()
        self.service = None

    def add_service(self, service: Service):
        """Add the service for testing"""

        self.service = service

    def sdo_read(self, index: [int, str], subindex: [None, int, str]):
        """Call a internal SDO read for testing"""

        co_node = self.node._node
        domain = canopen.objectdictionary.DOMAIN

        if subindex is None:
            if co_node.object_dictionary[index].data_type == domain:
                ret = co_node.sdo[index].raw
            else:
                ret = co_node.sdo[index].phys
        else:
            if co_node.object_dictionary[index][subindex].data_type == domain:
                ret = co_node.sdo[index][subindex].raw
            else:
                ret = co_node.sdo[index][subindex].phys

        return ret

    def sdo_write(self, index: [int, str], subindex: [None, int, str], value):
        """Call a internal SDO write for testing"""

        co_node = self.node._node
        domain = canopen.objectdictionary.DOMAIN

        if subindex is None:
            if co_node.object_dictionary[index].data_type == domain:
                co_node.sdo[index].raw = value
            else:
                co_node.sdo[index].phys = value
        else:
            if co_node.object_dictionary[index][subindex].data_type == domain:
                co_node.sdo[index][subindex].raw = value
            else:
                co_node.sdo[index][subindex].phys = value

    def start(self):
        """Start the mocked node."""
        self.service.start(self.node)

    def stop(self):
        """Stop the mocked node."""
        self.service.stop()
        self.node._destroy_node()
        self.node.stop()
