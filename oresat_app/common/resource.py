'''The OreSat Linux base app resource'''

import canopen
from loguru import logger


class Resource:
    '''OreSat Linux base app resource.

    All the `on_*` members can be overriden as needed.
    '''

    def __init__(self, node: canopen.LocalNode, name: str, delay: float = 1.0):
        '''
        Parameters
        ----------
        node: canopen.LocalNode
            The CANopen node. Gives acces object dictionary.
        name: str
            Unique name for the resource
        delay: float
            Delay between loop calls in seconds. Set to a negative number if loop is not needed
        '''

        self._node = node
        self._name = name
        self._delay = delay

        node.add_read_callback(self.on_read)
        node.add_write_callback(self.on_write)

    def on_start(self):
        '''Start the resource. Should be used to setup hardware or anything that is slow.'''

        pass

    def on_loop(self):
        '''This is called all in loop every :py:data:`delay` seconds, if :py:data:`delay` is a
        non-negative.'''

        pass

    def on_end(self):
        '''Called when the program ends and if the resources fails. Should be used to stop hardware and
        can be used to zero/clear resource's data in object dictionary as needed.'''

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

    @property
    def node(self) -> canopen.LocalNode:
        '''canopen.LocalNode: The local node to be used by the resource. Gives acces to object
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
