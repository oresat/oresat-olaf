from os import geteuid
from time import time, clock_settime, CLOCK_REALTIME

import canopen
from loguru import logger

from ..common.app import App
from ..common.ecss import scet_int_from_time, utc_int_from_time, scet_int_to_time, utc_int_to_time


class ECSSApp(App):

    def __init__(self, node: canopen.LocalNode):

        super().__init__('ESCC', -1.0)

        self.node = node
        self.index_scet = 0x2010
        self.index_utc = 0x2011

        node.add_read_callback(self.on_read)
        node.add_write_callback(self.on_write)

    def on_read(self, index: int, subindex: int, od: canopen.ObjectDictionary) -> bytes:

        ret = None

        if index == self.index_scet:
            ret = scet_int_from_time(time())
        elif index == self.index_utc:
            ret = utc_int_from_time(time())

        return ret

    def on_write(self, index: int, subindex: int, od: canopen.ObjectDictionary, data: bytes):

        if index == self.index_scet:
            raw = self.node.object_dictionary[self.index_scet].decode_raw(data)
            ts = scet_int_to_time(raw)
        elif index == self.index_utc:
            raw = self.node.object_dictionary[self.index_utc].decode_raw(data)
            ts = utc_int_to_time(raw)
        else:
            return

        if geteuid() == 0:
            clock_settime(CLOCK_REALTIME, ts)
            logger.info(f'{self.name} app has set system time')
        else:
            logger.error(f'{self.name} app cannot set time, not running as root')
