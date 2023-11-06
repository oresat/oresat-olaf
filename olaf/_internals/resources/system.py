"""Resource for the system."""
import psutil

from ...common.resource import Resource
from ..node import NodeStop


class SystemResource(Resource):
    """Resource for the system."""

    def on_start(self):
        self.node.od["system"]["reset"].value = 0

        self.node.add_sdo_callbacks("system", "ram_percent", self.on_read_ram, None)
        self.node.add_sdo_callbacks("system", "storage_percent", self.on_read_storage, None)
        self.node.add_sdo_callbacks("system", "reset", None, self.on_write_reset)

    def on_read_ram(self):
        """SDO read callback for getting the RAM usage percent."""

        return int(psutil.virtual_memory().percent)

    def on_read_storage(self):
        """SDO read callback for getting the storage usage percent."""

        return int(psutil.disk_usage("/").percent)

    def on_write_reset(self, value: int):
        """SDO write callback for resetting the system."""

        self.node.stop(NodeStop(value))
