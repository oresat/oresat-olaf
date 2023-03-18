from threading import Event

import canopen
from olaf import Resource, OreSatFileCache, logger
from olaf._internals.node import Node

logger.disable('olaf')


class MockNode(Node):

    def __init__(self):
        self.node = canopen.LocalNode(0x10, 'olaf/_internals/data/oresat_app.eds')
        super().__init__(self.node, None)

        self._fread_cache = OreSatFileCache('/tmp/fread')
        self._fread_cache.clear()
        self._fwrite_cache = OreSatFileCache('/tmp/fwrite')
        self._fwrite_cache.clear()

    def send_tpdo(self, tpdo: int) -> bool:

        return True  # override to do nothing


class MockApp:

    def __init__(self):
        super().__init__()
        self.node = MockNode()

    def add_resource(self, resource: Resource):
        '''Add the resource for testing'''

        self.resource = resource

    def sdo_read(self, index: [int, str], subindex: [None, int, str]):
        '''Call a internal SDO read for testing'''

        co_node = self.node.node
        domain = canopen.objectdictionary.DOMAIN

        if subindex is None:
            if co_node.object_dictionary[index].data_type == domain:
                return co_node.sdo[index].raw
            else:
                return co_node.sdo[index].phys
        else:
            if co_node.object_dictionary[index][subindex].data_type == domain:
                return co_node.sdo[index][subindex].raw
            else:
                return co_node.sdo[index][subindex].phys

    def sdo_write(self, index: [int, str], subindex: [None, int, str], value):
        '''Call a internal SDO write for testing'''

        co_node = self.node.node
        domain = canopen.objectdictionary.DOMAIN

        if subindex is None:
            if co_node.object_dictionary[index].data_type == domain:
                co_node.sdo[index].raw = value
            else:
                co_node.sdo[index].phys = value
        else:
            if co_node.object_dictionary[index][subindex].data_type == domain:
                co_node.sdo[index][subindex].raw = value
            else:
                co_node.sdo[index][subindex].phys = value

    def start(self):

        self.resource.start(self.node)

    def stop(self):

        self.resource.end()
