"""OLAF App."""

import os
import signal
import subprocess
from typing import Union

import canopen
from loguru import logger

from ..canopen.master_node import MasterNode
from ..canopen.network import CanNetwork
from ..canopen.node import Node, NodeStop
from ..common.resource import Resource
from ..common.service import Service
from .resources.ecss import EcssResource
from .resources.fread import FreadResource
from .resources.fwrite import FwriteResource
from .resources.system import SystemResource
from .services.logs import LogsService
from .services.os_command import OsCommandService
from .services.updater import UpdaterService
from .updater import Updater


class App:
    """
    The application class that manages the CANopen node and resources.

    Use the global ``olaf.app`` obect.
    """

    def __init__(self):
        self._od = None
        self._resources = []
        self._services = []
        self._node = None
        self._updater = None
        self._factory_reset_cb = None

    def __del__(self):
        self.stop()

    def _quit(self, signo, _frame):
        """Called when signals are caught"""

        logger.debug(f"signal {signal.Signals(signo).name} was caught")
        self.stop()

    def setup(
        self,
        network: CanNetwork,
        od: canopen.ObjectDictionary,
        master_od_db: Union[dict, None] = None,
        load_core: bool = True,
    ):
        """
        Setup the app. Will be called by ``olaf_setup`` automatically.

        Parameters
        ----------
        network: CanNetwork
            The CAN network to use.
        od: canopen.ObjectDictionary
            The nodes object dictionary.
        master_od_db: dict
            Master node od database. Only for the C3.
        load_core: bool
            Load the core olaf services and resources

        Raises
        ------
        ValueError
            Invalid parameter(s)
        """

        self._od = od

        if master_od_db:
            self._node = MasterNode(network, self._od, master_od_db)
        else:
            self._node = Node(network, self._od)

        # setup updater
        self._updater = Updater(
            f"{self._node.work_base_dir}/updater", f"{self._node.cache_base_dir}/updates"
        )

        if load_core:
            # default core services
            self.add_service(UpdaterService(self._updater))
            self.add_service(LogsService())
            self.add_service(OsCommandService())

            # default core resources
            self.add_resource(EcssResource())
            self.add_resource(SystemResource())
            self.add_resource(FreadResource())
            self.add_resource(FwriteResource())
            # self.add_resource(DaemonsResource())

    def add_resource(self, resource: Resource):
        """
        Add a resource for the app

        Parameters
        ----------
        resource: Resource
            The resource to add.
        """

        self._resources.append(resource)

    def add_service(self, service: Service):
        """
        Add a resource for the app

        Parameters
        ----------
        service: Service
            The service to add.
        """

        self._services.append(service)

    def run(self):
        """Run the app."""

        # setup event
        for sig in ["SIGTERM", "SIGHUP", "SIGINT"]:
            signal.signal(getattr(signal, sig), self._quit)

        logger.info(f"{self._node.name} app is starting")

        for service in self._services:
            service.start(self._node)

        for resource in self._resources:
            resource.start(self._node)

        if self.node is None:
            logger.critical("node was not set")
            return

        try:
            reset = self._node.run()
        except Exception as e:  # pylint: disable=W0718
            logger.exception(f"unexpected error was raised by app node: {e}")
            reset = NodeStop.SOFT_RESET

        for service in self._services:
            service.stop()

        for resource in self._resources:
            resource.end()

        logger.info(f"{self._node.name} app has ended")

        if reset == NodeStop.HARD_RESET:
            logger.info("hard reseting the system")

            if os.geteuid() == 0:  # running as root
                subprocess.run("reboot", shell=True, check=False)
            else:
                logger.error("not running as root, cannot reboot the system")
        elif reset == NodeStop.FACTORY_RESET:
            logger.info("factory reseting the system")

            # clear caches
            self._node.fread_cache.clear()
            self._node.fwrite_cache.clear()
            self._updater.clear_cache()

            # run custom factory reset function
            try:
                if self._factory_reset_cb:
                    self._factory_reset_cb()
            except Exception as e:  # pylint: disable=W0718
                logger.exception(f"custom factory reset function raised: {e}")

            if os.geteuid() == 0:  # running as root
                subprocess.run("reboot", shell=True, check=False)
            else:
                logger.error("not running as root, cannot reboot the system")
        elif reset == NodeStop.POWER_OFF:
            logger.info("powering off the system")

            if os.geteuid() == 0:  # running as root
                subprocess.run("poweroff", shell=True, check=False)
            else:
                logger.error("not running as root, cannot power off the system")

    def stop(self):
        """End the run loop"""

        if self._node:
            self._node.stop()

    @property
    def node(self) -> Node:
        """Node: The CANopen node."""

        return self._node

    def set_factory_reset_callback(self, cb_func):
        """Set a custom factory reset callback function."""

        self._factory_reset_cb = cb_func

    @property
    def od(self) -> canopen.ObjectDictionary:
        """canopen.ObjectDictionary: The node's Object Dictionary."""

        return self._od


app = App()
"""The global instance of the OLAF app."""
