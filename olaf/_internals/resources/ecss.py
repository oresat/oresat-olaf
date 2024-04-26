"""Resource for ECSS CANBus Extended Protocal standards"""

from os import geteuid
from time import CLOCK_REALTIME, clock_settime, time

from loguru import logger

from ...canopen.ecss import scet_int_from_time, scet_int_to_time, utc_int_from_time, utc_int_to_time
from ...common.resource import Resource


class EcssResource(Resource):
    """Resource for ECSS CANBus Extended Protocal standards"""

    def on_start(self):
        self.node.add_sdo_callbacks("scet", None, self.on_scet_read, self.on_scet_write)
        self.node.add_sdo_callbacks("utc", None, self.on_utc_read, self.on_utc_write)

    def on_scet_read(self) -> int:
        """SDO read callback to get system time as a SCET time stamp."""

        return scet_int_from_time(time())

    def on_scet_write(self, value: int):
        """SDO write callback to set the system time from SCET time stamp."""

        ts = scet_int_to_time(value)
        self._set_time(ts)

    def on_utc_read(self) -> int:
        """SDO read callback to get system time as a UTC time stamp."""

        return utc_int_from_time(time())

    def on_utc_write(self, value: int):
        """SDO write callback to set the system time from UTC time stamp."""

        ts = utc_int_to_time(value)
        self._set_time(ts)

    def _set_time(self, ts: float):
        """set the system time"""

        if geteuid() == 0:
            clock_settime(CLOCK_REALTIME, ts)
            logger.info(f"{self.__class__.__name__} resource has set system time")
        else:
            logger.error(
                f"{self.__class__.__name__} resource cannot set system time, not running " "as root"
            )
