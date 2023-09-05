'''Resource for about the local system.'''
import psutil

from ..node import NodeStop
from ...common.resource import Resource


class SystemResource(Resource):
    '''Resource for about the local system.'''

    def on_start(self):

        self.node.od['common_data']['reset'].value = 0

        self.node.add_sdo_callbacks('common_data', 'ram_percent', self.on_read_ram, None)
        self.node.add_sdo_callbacks('common_data', 'storage_percent', self.on_read_storage, None)
        self.node.add_sdo_callbacks('common_data', 'reset', None, self.on_write_reset)

    def on_read_ram(self):
        '''SDO read callback for getting the RAM usage percent.'''

        return int(psutil.virtual_memory().percent)

    def on_read_storage(self):
        '''SDO read callback for getting the storage usage percent.'''

        return int(psutil.disk_usage('/').percent)

    def on_write_reset(self, value: int):

        self.node.stop(NodeStop(value))
