from os import geteuid
from time import time, clock_settime, CLOCK_REALTIME

from loguru import logger

from ...common.resource import Resource
from ...common.ecss import scet_int_from_time, utc_int_from_time, scet_int_to_time, utc_int_to_time


class ECSSResource(Resource):
    '''Resource for ECSS CANBus Extended Protocal standards'''

    def __init__(self):
        super().__init__()

        self.scet_index = 0x2010
        self.utc_index = 0x2011

    def on_start(self):

        self.node.add_sdo_read_callback(self.scet_index, self.on_scet_read)
        self.node.add_sdo_write_callback(self.scet_index, self.on_scet_write)
        self.node.add_sdo_read_callback(self.utc_index, self.on_utc_read)
        self.node.add_sdo_write_callback(self.utc_index, self.on_utc_write)

    def on_scet_read(self, index: int, subindex: int):

        return scet_int_from_time(time())

    def on_scet_write(self, index: int, subindex: int, value):

        ts = scet_int_to_time(value)
        self._set_time(ts)

    def on_utc_read(self, index: int, subindex: int):

        return utc_int_from_time(time())

    def on_utc_write(self, index: int, subinde: int, value):

        ts = utc_int_to_time(value)
        self._set_time(ts)

    def _set_time(self, ts: float):
        if geteuid() == 0:
            clock_settime(CLOCK_REALTIME, ts)
            logger.info(f'{self.__class__.__name__} resource has set system time')
        else:
            logger.error(f'{self.__class__.__name__} resource cannot set system time, not running '
                         'as root')
