from os import geteuid
from time import time, clock_settime, CLOCK_REALTIME

from loguru import logger

from ...common.resource import Resource
from ...common.ecss import scet_int_from_time, utc_int_from_time, scet_int_to_time, utc_int_to_time


class ECSSResource(Resource):
    '''Resource for ECSS CANBus Extended Protocal standards'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scet_index = 0x2010
        self.utc_index = 0x2011

    def on_start(self):
        self.scet_obj = self.od[self.scet_index]
        self.utc_obj = self.od[self.utc_index]

    def on_read(self, index, subindex, od):

        ret = None

        if index == self.scet_index:
            ret = scet_int_from_time(time())
        elif index == self.utc_index:
            ret = utc_int_from_time(time())

        return ret

    def on_write(self, index, subindex, od, data):

        if index == self.scet_index:
            raw = self.scet_obj.decode_raw(data)
            ts = scet_int_to_time(raw)
        elif index == self.utc_index:
            raw = self.utc_index.decode_raw(data)
            ts = utc_int_to_time(raw)
        else:
            return  # write is not for these indexes

        if geteuid() == 0:
            clock_settime(CLOCK_REALTIME, ts)
            logger.info(f'{self.name} resource has set system time')
        else:
            logger.error(f'{self.name} resource cannot set time, not running as root')
