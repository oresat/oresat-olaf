'''The OreSat Linux base app resource'''
from typing import Any

import canopen
from loguru import logger

from .oresat_file_cache import OreSatFileCache


class Resource:
    '''OreSat Linux app resource.

    All the ``on_*`` members can be overridden as needed.
    '''

    def __init__(self, fread_cache: OreSatFileCache, fwrite_cache: OreSatFileCache,
                 mock_hw: bool, send_tpdo):
        '''
        Parameters
        ----------
        fread_cache: OreSatFileCache
            The file read over CAN cache (the file cache a master node can read from).
        fwrite_cache: OreSatFileCache
            The file write over CAN cache (the file cache a master node can write to).
        mock_hw: bool
            Resource should mock any hardware when set to ``True``.
        send_tpdo
            function callback for :py:func:`App.send_tpdo`.
        '''

        self._od = None
        self._fread_cache = fread_cache
        self._fwrite_cache = fwrite_cache
        self._mock_hw = mock_hw
        self._send_tpdo_cb = send_tpdo

    def start(self, node: canopen.LocalNode):
        '''
        App will call this to start the resource. This will call `self.on_start()` after the
        `self.od` is set. Initialize any values in the OD here, not in the constructor.

        Parameters
        ----------
        node: canopen.LocalNode
            The CANopen node. Gives acces object dictionary.
        '''
        logger.debug(f'starting resource {self.__class__.__name__}')

        self._od = node.object_dictionary
        node.add_read_callback(self.on_read)
        node.add_write_callback(self.on_write)

        try:
            self.on_start()
        except Exception as exc:
            logger.critical(f'{self.__class__.__name__}\'s on_start raised an uncaught exception:'
                            f'{exc}')

    def end(self):
        '''
        App will call this to stop the resource. This will call `self.on_end()`.
        '''

        logger.debug(f'stopping resource {self.__class__.__name__}')

        try:
            self.on_end()
        except Exception as exc:
            logger.critical(f'{self.__class__.__name__}\'s on_end raised an uncaught exception:'
                            f' {exc}')

    def on_start(self) -> None:
        '''Start the resource. Should be used to setup hardware or anything that is slow.'''

        pass

    def on_end(self) -> None:
        '''Called when the program ends and if the resources fails. Should be used to stop hardware
        and can be used to zero/clear resource's data in object dictionary as needed.'''

        pass

    def on_read(self, index: int, subindex: int, od: canopen.objectdictionary.Variable) -> Any:
        '''SDO read callback function. Allows overriding the data being sent on a SDO read. Return
        valid datatype for object, if overriding read data, or :py:data:`None` to use the the value
        on object dictionary.

        Parameters
        ----------
        index: int
            The index the SDO is reading to.
        subindex: int
            The subindex the SDO is reading to.
        od: canopen.objectdictionary.Variable
            The variable object being read tp. Badly named.

        Returns
        -------
        Any
            The value to return for that index / subindex. Return :py:data:`None` if invalid index
            / subindex.
        '''

        pass

    def on_write(self, index: int, subindex: int, od: canopen.objectdictionary.Variable,
                 data: bytes):
        '''SDO write callback function. Gives access to the data being received on a SDO write.

        *Note:* data is still written to object dictionary before call.

        Parameters
        ----------
        index: int
            The index the SDO being written to.
        subindex: int
            The subindex the SDO being written to.
        od: canopen.objectdictionary.Variable
            The variable object being written to. Badly named.
        data: bytes
            The raw data being written.
        '''

        pass

    def send_tpdo(self, tpdo: int):
        '''Send a TPDO. Will not be sent if not node is not in operational state.

        Parameters
        ----------
        tpdo: int
            TPDO number to send.
        '''

        self._send_tpdo_cb(tpdo)

    @property
    def mock_hw(self):
        '''bool: Resource should mock all hardware when set to ``True``. :py:class:`App` will set
        this based of runtime args.
        '''

        return self._mock_hw

    @property
    def od(self):
        '''canopen.ObjectDictionary: Access the object dictionary.'''

        return self._od

    @property
    def fread_cache(self):
        '''OreSatFileCache: The file read over CAN cache (the file cache a master node can read
        from). Resources can add files to this cache to have them transfer to the master node.
        '''

        return self._fread_cache

    @property
    def fwrite_cache(self):
        '''OreSatFileCache: The file write over CAN cache (the file cache a master node can write
        to). Resources can consume files from this cache that were transfer from the master node to
        the app.
        '''

        return self._fwrite_cache
