'''The OreSat Linux base app resource'''
from typing import Any

import canopen
from loguru import logger

from .oresat_file_cache import OreSatFileCache


class Resource:
    '''OreSat Linux base app resource.

    All the `on_*` members can be overridden as needed.

    Derived class must set `self.delay` if `on_loop` functionality is wanted.
    '''

    def __init__(
        self,
        node: canopen.LocalNode,
        fread_cache: OreSatFileCache,
        fwrite_cache: OreSatFileCache
    ):
        '''
        Parameters
        ----------
        node: canopen.LocalNode
            The CANopen node. Gives acces object dictionary.
        fread_cache: OreSatFileCache
            The file read over CAN cache (the file cache a master node can read from).
        fwrite_cache: OreSatFileCache
            The file write over CAN cache (the file cache a master node can write to).
        '''

        self.delay = -1
        self.od = node.object_dictionary
        self.fread_cache = fread_cache
        self.fwrite_cache = fwrite_cache

        node.add_read_callback(self.on_read)
        node.add_write_callback(self.on_write)

    def on_start(self) -> None:
        '''Start the resource. Should be used to setup hardware or anything that is slow.'''

        pass

    def on_loop(self) -> None:
        '''This is called all in loop every :py:data:`delay` seconds, if :py:data:`delay` is set
        to a non-negative number.'''

        pass

    def on_end(self) -> None:
        '''Called when the program ends and if the resources fails. Should be used to stop hardware and
        can be used to zero/clear resource's data in object dictionary as needed.'''

        pass

    def on_read(self, index: int, subindex: int, od: canopen.objectdictionary.Variable) -> Any:
        '''SDO read callback function. Allows overriding the data being sent on a SDO read. Return
        valid datatype for object, if overriding read data, or None to use the the value on object
        dictionary.

        Parameters
        ----------
        index: int
            The index the SDO is reading to.
        subindex: int
            The subindex the SDO is reading to.
        od: canopen.object_dictionary.Variable
            The variable object being read tp. Badly named.
        '''

        pass

    def on_write(
        self,
        index: int,
        subindex: int, od:
        canopen.objectdictionary.Variable,
        data: bytes
    ) -> None:
        '''SDO write callback function. Gives access to the data being received on a SDO write.

        *Note:* data is still written to object dictionary before call.

        Parameters
        ----------
        index: int
            The index the SDO being written to.
        subindex: int
            The subindex the SDO being written to.
        od: canopen.object_dictionary.Variable
            The variable object being written to. Badly named.
        data: bytes
            The raw data being written.
        '''

        pass
