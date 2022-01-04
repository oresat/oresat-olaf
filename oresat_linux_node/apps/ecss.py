
from time import time

import canopen

from ..common.app import App
from ..common.ecss import scet_int_from_time


class ECSSApp(App):

    def __init__(self, node: canopen.LocalNode):

        super().__init__('ESCC', -1.0)

        self.index_scet = 0x2010
        self.index_utc = 0x2011

        node.add_read_callback(self.on_read)

    def on_read(self, index: int, subindex: int, od: canopen.ObjectDictionary) -> bytes:

        ret = None

        if index == self.index_scet:
            ret = scet_int_from_time(time())

        return ret
