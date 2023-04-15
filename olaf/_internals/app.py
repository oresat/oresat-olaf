import signal
from os.path import abspath, dirname

import canopen
from loguru import logger

from ..common.resource import Resource
from .node import Node
from .master_node import MasterNode
from .resources.os_command import OSCommandResource
from .resources.system_info import SystemInfoResource
from .resources.file_caches import FileCachesResource
from .resources.fread import FreadResource
from .resources.fwrite import FwriteResource
from .resources.ecss import ECSSResource
from .resources.updater import UpdaterResource
from .resources.logs import LogsResource
from .resources.store_eds import StoreEdsResource


class App:
    '''
    The application class that manages the CAN bus and resources.

    Use the global ``olaf.app`` obect.
    '''

    _BACKUP_EDS = abspath(dirname(__file__)) + '/data/oresat_app.eds'
    '''Internal eds file incase app's is misformatted or missing.'''

    def __init__(self):

        self._bus = None
        self._resources = []
        self._network = None
        self._node = None
        self._app_node = None

        # setup event
        for sig in ['SIGTERM', 'SIGHUP', 'SIGINT']:
            signal.signal(getattr(signal, sig), self._quit)

    def __del__(self):

        self.stop()

    def _quit(self, signo, _frame):
        '''Called when signals are caught'''

        logger.debug(f'signal {signal.Signals(signo).name} was caught')
        self.stop()

    def _load_node(self, node_id: int, eds: str):

        dcf_node_id = canopen.import_od(eds).node_id
        if node_id != 0:
            self._node_id = node_id
        elif dcf_node_id:
            self._node_id = dcf_node_id
        else:
            self._node_id = 0x7C
        self._node = canopen.LocalNode(self._node_id, eds)
        self._node.object_dictionary.node_id = self._node_id
        self._node.object_dictionary.bitrate = 1_000_000  # oresat node will always have 1 Mbps

    def setup(self, eds: str, bus: str, node_id: [int, str] = 0, master_node: bool = False):
        '''
        Setup the app. Will be called by ``olaf_setup`` automatically.

        Parameters
        ----------
        eds: str
            File path to EDS or DCF file.
        bus: str
            Which CAN bus to use.
        node_id: int, str
            The node ID. If set to 0 and DCF was used for the eds arg, the value will be pulled
            from the DCF, otherwise, it will be set to 0x7C.
        master_node: bool
            Node is a master node.

        Raises
        ------
        ValueError
            Invalid parameter(s)
        '''

        if isinstance(node_id, str):
            if node_id.startswith('0x'):
                node_id = int(node_id, 16)
            else:
                node_id = int(node_id)
        elif not isinstance(node_id, int):
            raise ValueError('node_id is not a int/hex str or a int')

        if eds is not None:
            try:
                self._load_node(node_id, eds)
            except Exception as e:
                logger.error(f'{e.__class__.__name__}: {e}')
                logger.warning(f'failed to read in {eds}, using OLAF\'s internal eds as backup')
                eds = self._BACKUP_EDS
                self._load_node(node_id, eds)
        else:
            logger.warning('No eds or dcf was supplied, using OLAF\'s internal eds')
            eds = self._BACKUP_EDS
            self._load_node(node_id, eds)

        self._name = self._node.object_dictionary.device_information.product_name

        if master_node:
            self._app_node = MasterNode(self._node, bus)
        else:
            self._app_node = Node(self._node, bus)

        # default resources
        self.add_resource(OSCommandResource())
        self.add_resource(ECSSResource())
        self.add_resource(SystemInfoResource())
        self.add_resource(FileCachesResource())
        self.add_resource(FreadResource())
        self.add_resource(FwriteResource())
        self.add_resource(UpdaterResource())
        self.add_resource(LogsResource())
        self.add_resource(StoreEdsResource(eds))

    def add_resource(self, resource: Resource):
        '''
        Add a resource for the app

        Parameters
        ----------
        resource: Resource
            The resource to add.
        '''

        self._resources.append(resource)

    def run(self):
        logger.info(f'{self._app_node.name} app is starting')

        for resource in self._resources:
            resource.start(self._app_node)

        if self._app_node:
            try:
                self._app_node.run()
            except Exception as e:
                logger.critical(f'unexpected error was raised by app node: {e}')

        for resource in self._resources:
            resource.end()

        logger.info(f'{self._app_node.name} app has ended')

    def stop(self):
        '''End the run loop'''

        if self._app_node:
            self._app_node.stop()

    @property
    def node(self) -> Node:
        return self._app_node


app = App()
'''The global instance of the OLAF app.'''
