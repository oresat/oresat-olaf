import os
import signal
import subprocess
from os.path import abspath, dirname

import canopen
from loguru import logger

from ..common.resource import Resource
from .node import Node, NodeStop
from .master_node import MasterNode
from .updater import Updater
from .resources.os_command import OSCommandResource
from .resources.system_info import SystemInfoResource
from .resources.file_caches import FileCachesResource
from .resources.fread import FreadResource
from .resources.fwrite import FwriteResource
from .resources.ecss import ECSSResource
from .resources.updater import UpdaterResource
from .resources.logs import LogsResource
from .resources.store_eds import StoreEdsResource
from .resources.power_control import PowerControlResource


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
        self._updater = None
        self._factory_reset_cb = None

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

        # setup updater
        self._updater = Updater(f'{self._app_node.work_base_dir}/updater',
                                f'{self._app_node.cache_base_dir}/updates')

        # default resources
        self.add_resource(OSCommandResource())
        self.add_resource(ECSSResource())
        self.add_resource(SystemInfoResource())
        self.add_resource(FileCachesResource())
        self.add_resource(FreadResource())
        self.add_resource(FwriteResource())
        self.add_resource(UpdaterResource(self._updater))
        self.add_resource(LogsResource())
        self.add_resource(StoreEdsResource(eds))
        self.add_resource(PowerControlResource())

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
                reset = self._app_node.run()
            except Exception as e:
                logger.critical(f'unexpected error was raised by app node: {e}')
                reset = NodeStop.SOFT_RESET

        for resource in self._resources:
            resource.end()

        logger.info(f'{self._app_node.name} app has ended')

        if reset == NodeStop.HARD_RESET:
            logger.info('hard reseting the system')

            if os.geteuid() == 0:  # running as root
                subprocess.run('reboot', shell=True)
            else:
                logger.error('not running as root, cannot reboot the system')
        elif reset == NodeStop.FACTORY_RESET:
            logger.info('factory reseting the system')

            # clear caches
            self._app_node.fread_cache.clear()
            self._app_node.fwrite_cache.clear()
            self._updater.clear_cache()

            # run custom factory reset function
            try:
                if self._factory_reset_cb:
                    self._factory_reset_cb()
            except Exception as e:
                logger.error(f'custom factory reset function raised: {e}')

            if os.geteuid() == 0:  # running as root
                subprocess.run('reboot', shell=True)
            else:
                logger.error('not running as root, cannot reboot the system')
        elif reset == NodeStop.POWER_OFF:
            logger.info('powering off the system')

            if os.geteuid() == 0:  # running as root
                subprocess.run('poweroff', shell=True)
            else:
                logger.error('not running as root, cannot power off the system')

    def stop(self):
        '''End the run loop'''

        if self._app_node:
            self._app_node.stop()

    @property
    def node(self) -> Node:
        return self._app_node

    def set_factory_reset_callback(self, cb_func):
        '''Set a custom factory reset callback function.'''

        self._factory_reset_cb = cb_func


app = App()
'''The global instance of the OLAF app.'''
