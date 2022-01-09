'''OreSat Linux node app'''

from threading import Event

import canopen
from loguru import logger


class App:
    '''OreSat Linux node base app.

    All the `on_*` members can be overriden as needed.
    '''

    def __init__(self, node: canopen.LocalNode, name: str, delay: float = 1.0):
        '''
        Parameters
        ----------
        node: canopen.LocalNode
            The CANopen node. Gives acces object dictionary.
        name: str
            Unique name for the app
        delay: float
            Delay between loop calls in seconds. Set to a negative number if loop is not needed
        '''

        self._node = node
        self._name = name
        self._delay = delay

        node.add_read_callback(self.on_read)
        node.add_write_callback(self.on_write)

    def on_start(self):
        '''Start the app. Should be used to setup hardware or anything that is slow.'''

        pass

    def on_loop(self):
        '''This is called all in loop every :py:data:`delay` seconds, if :py:data:`delay` is a
        non-negative.'''

        pass

    def on_end(self):
        '''Called when the program ends and if the apps fails. Should be used to stop hardware and
        can be used to zero/clear app's data in object dictionary as needed.'''

        pass

    def on_read(self, index: int, subindex: int, od: canopen.objectdictionary.Variable):
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

    def on_write(self,
                 index: int,
                 subindex: int, od:
                 canopen.objectdictionary.Variable,
                 data: bytes):
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

    def start(self):
        '''Starts the app. Calls :py:func:`on_start` and handles any exceptions raised.'''

        logger.info(f'starting {self._name} app')
        try:
            self.on_start()
        except Exception as exc:
            logger.critical(f'{self._name} app\'s  on_start raised an uncaught exception: {exc}')
            return  # don't continue

    def run(self, event: Event):
        '''Runs the app. Will call :py:func:`on_loop` every :py:data:`delay` seconds. If the app fails
        :py:func:`end` will be called.

        Parameters
        ----------
        event: threading.Event
            The end event. Run loop will end when event is set.
        '''

        if self._delay < 0:
            return

        while not event.is_set():
            try:
                self.on_loop()
            except Exception as exc:  # nothing fancy just end return if the app loop fails
                logger.critical(f'{self._name} app\'s on_loop raised an uncaught exception: {exc}')
                self.end()
                break

            event.wait(self._delay)

    def end(self):
        '''Ends the app. Calls :py:func:`on_end` and handles any exceptions raised.'''

        logger.info(f'ending {self._name} app')
        try:
            self.on_end()
        except Exception as exc:
            logger.critical(f'{self._name} app\'s on_end raised an uncaught exception: {exc}')

    @property
    def node(self) -> canopen.LocalNode:
        '''canopen.LocalNode: The local node to be used by the app. Gives acces to object
        dictionary.'''

        return self._node

    @property
    def name(self) -> str:
        '''str: App's unique name.'''

        return self._name

    @property
    def delay(self) -> float:
        '''float: Delay between :py:func:`on_loop` calls. If it is a negative number
        :py:func:`on_loop` will not be called.'''

        return self._delay
