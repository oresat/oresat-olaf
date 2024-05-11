"""Resource for the system."""

from time import monotonic, time

import psutil
from loguru import logger

from ...board.eeprom import Eeprom
from ...canopen.node import NodeStop
from ...common.resource import Resource


class SystemResource(Resource):
    """Resource for the system."""

    def on_start(self):
        self.node.od_write("system", "reset", 0)

        self.node.add_sdo_callbacks("system", "ram_percent", self.on_read_ram, None)
        self.node.add_sdo_callbacks("system", "storage_percent", self.on_read_storage, None)
        self.node.add_sdo_callbacks("system", "uptime", self.on_read_uptime, None)
        self.node.add_sdo_callbacks("system", "unix_time", self.on_read_unix_time, None)
        self.node.add_sdo_callbacks("system", "reset", None, self.on_write_reset)

        try:
            eeprom = Eeprom()
            self.node.od_write("versions", "hw_version", f"{eeprom.major}.{eeprom.minor}")
        except (PermissionError, FileNotFoundError):
            logger.warning("could not read hardware info from eeprom")

    def on_read_ram(self):
        """SDO read callback for getting the RAM usage percent."""

        return int(psutil.virtual_memory().percent)

    def on_read_storage(self):
        """SDO read callback for getting the storage usage percent."""

        return int(psutil.disk_usage("/").percent)

    def on_read_uptime(self):
        """SDO read callback for getting the uptime."""

        return int(monotonic())

    def on_read_unix_time(self):
        """SDO read callback for getting the current unix time."""

        return int(time())

    def on_write_reset(self, value: int):
        """SDO write callback for resetting the system."""

        if value in list(NodeStop):
            self.node.stop(NodeStop(value))
