import sys
import struct
import signal
from os import geteuid
from pathlib import Path
from threading import Thread, Event

import canopen
import psutil
from loguru import logger

from .common.app import App
from .common.oresat_file_cache import OreSatFileCache
from .apps.os_command import OSCommandApp
from .apps.system_info import SystemInfoApp
from .apps.file_caches import FileCachesApp
from .apps.fread import FreadApp
from .apps.fwrite import FwriteApp
from .apps.ecss import ECSSApp
from .apps.updater import UpdaterApp
from .apps.logs import LogsApp


class OreSatNode:
    '''The main class that manages the CAN bus, apps, and threads.'''

    def __init__(self, eds: str, bus: str, node_id: int = 0):
        '''
        Parameters
        ----------
        eds: str
            File path to EDS or DCF file.
        bus: str
            Which CAN bus to use.
        node_id: int
            The node ID. If not set and a DCF was used for the eds arg, the value will be pulled
            from the DCD, otherwise, it will be set to 0x7C.
        '''

        self.bus = bus
        self.event = Event()
        self.apps = []

        if geteuid() == 0:  # running as root
            self.work_base_dir = '/var/lib/oresat'
            self.cache_base_dir = '/var/cache/oresat'
        else:
            self.work_base_dir = str(Path.home()) + '/.oresat'
            self.cache_base_dir = str(Path.home()) + '/.cache/oresat'

        self.fread_cache = OreSatFileCache(self.cache_base_dir + '/fread')
        self.fwrite_cache = OreSatFileCache(self.cache_base_dir + '/fwrite')

        # setup event
        for sig in ['SIGTERM', 'SIGHUP', 'SIGINT']:
            signal.signal(getattr(signal, sig), self._quit)

        self.network = canopen.Network()
        self.network.connect(bustype='socketcan', channel=self.bus)
        dcf_node_id = canopen.import_od(eds).node_id
        if node_id != 0:
            self.node_id = node_id
        elif dcf_node_id:
            self.node_id = dcf_node_id
        else:
            self.node_id = 0x7C
        self.node = canopen.LocalNode(self.node_id, eds)
        self.node.object_dictionary.node_id = self.node_id
        self.network.add_node(self.node)
        self.node.nmt.state = 'PRE-OPERATIONAL'

        self.node.tpdo.read()
        self.node.rpdo.read()

        # python canopen does not set the value to default for some reason
        for i in self.od:
            if not isinstance(self.od[i], canopen.objectdictionary.Variable):
                for j in self.od[i]:
                    self.od[i][j].value = self.od[i][j].default

        default_rpdos = [
            0x200 + self.node_id,
            0x300 + self.node_id,
            0x400 + self.node_id,
            0x500 + self.node_id
        ]
        default_tpdos = [
            0x180 + self.node_id,
            0x280 + self.node_id,
            0x380 + self.node_id,
            0x480 + self.node_id
        ]

        # fix COB-IDs for invaild PDOs
        #
        # all oresat node RPDO COB-ID follow values of 0x[2345]00 + $NODEID
        # all oresat node TPDO COB-ID follow values of 0x[1234]80 + $NODEID
        # this fixes the values for all 16 RPDOs/TPDOs
        for i in range(len(self.node.rpdo)):
            cob_id = self.od[0x1400 + i][1].default & 0xFFF
            if cob_id in default_rpdos:
                cob_id = 0x200 + 0x100 * (i % 4) + self.node_id + i // 4
            else:
                cob_id = self.od[0x1400 + i][1].default
            self.od[0x1400 + i][1].value = cob_id
        for i in range(len(self.node.tpdo)):
            cob_id = self.od[0x1800 + i][1].default & 0xFFF
            if cob_id in default_tpdos:
                cob_id = 0x180 + 0x100 * (i % 4) + self.node_id + i // 4
            else:
                cob_id = self.od[0x1800 + i][1].default
            self.od[0x1800 + i][1].value = cob_id

        # default apps
        self.add_app(OSCommandApp(self.node))
        self.add_app(ECSSApp(self.node))
        self.add_app(SystemInfoApp(self.node))
        self.add_app(FileCachesApp(self.node, self.fread_cache, self.fwrite_cache))
        self.add_app(FreadApp(self.node, self.fread_cache))
        self.add_app(FwriteApp(self.node, self.fwrite_cache))
        self.add_app(UpdaterApp(self.node,
                                self.fread_cache,
                                self.fwrite_cache,
                                self.work_base_dir + '/updater',
                                self.cache_base_dir + '/updater'))
        self.add_app(LogsApp(self.node, self.fread_cache))

    def __del__(self):

        self.stop()

        try:
            self.network.disconnect()
        except Exception as exc:
            logger.error(exc)

    def _quit(self, signo, _frame):
        '''called when signals are caught'''
        logger.info(f'signal {signal.Signals(signo).name} was caught')
        self.stop()

    def send_tpdo(self, tpdo: int):
        '''Send a TPDO. Will not be sent if not node is not in operational state.

        Parameters
        ----------
        tpdo: int
            TPDO number to send
        '''

        if self.node.nmt.state != 'OPERATIONAL':
            return  # PDOs should not be sent if not in OPERATIONAL state

        cob_id = self.od[0x1800 + tpdo][1].value
        maps = self.od[0x1A00 + tpdo][0].value

        data = b''
        for i in range(maps):
            pdo_map = self.od[0x1A00 + tpdo][i + 1].value
            if pdo_map == 0:
                break  # nothing todo
            pdo_map_bytes = pdo_map.to_bytes(4, 'big')
            index, subindex, length = struct.unpack('>HBB', pdo_map_bytes)
            value = self.node.sdo[index][subindex].phys  # to call sdo callback(s)
            value_bytes = self.od[index][subindex].encode_raw(value)
            data += value_bytes

        try:
            self.network.send_message(cob_id, data)
        except Exception:
            pass

    def _send_tpdo_loop(self, tpdo: int):

        while not self.event.is_set():
            self.send_tpdo(tpdo)

            # get event time
            value = self.od[0x1800 + tpdo][5].value

            # milliseconds as int to seconds as a float
            delay = float(value) / 1000

            self.event.wait(delay)

    def add_app(self, app):
        '''Add a app to be manage by `OreSatNode`'''

        logger.debug(f'adding {app.name} app')
        self.apps.append(app)

    def run(self):
        '''Go into operational mode, start all the apps, start all the threads, and monitor
        everything in a loop.'''

        logger.info('node is starting')

        self.node.nmt.start_heartbeat(self.od[0x1017].default)
        self.node.nmt.state = 'OPERATIONAL'
        tpdo_threads = []
        app_threads = []

        for app in self.apps:
            app.start()
            if app.delay >= 0:
                t = Thread(target=app.run, args=(self.event,))
                t.start()
                app_threads.append(t)

        for i in range(len(self.node.tpdo)):
            transmission_type = self.od[0x1800 + i][2].default
            event_time = self.od[0x1800 + i][5].default

            if transmission_type in [0xFE, 0xFF] and event_time and event_time > 0:
                t = Thread(target=self._send_tpdo_loop, args=(i,))
                t.start()
                tpdo_threads.append(t)

        logger.info('node is running')
        while not self.event.is_set():
            if not psutil.net_if_stats().get(self.bus).isup:
                logger.critical(f'CAN bus {self.bus} is down')
                if self.node.nmt.state != 'PRE-OPERATIONAL':
                    self.node.nmt.state == 'PRE-OPERATIONAL'

            # monitor threads
            for t in tpdo_threads:
                if not t.is_alive:
                    logger.info('tpdo thread has ended')
            for t in app_threads:
                if not t.is_alive:
                    logger.info('app thread has ended')

            self.event.wait(1)

        for app in self.apps:
            app.end()

        for t in tpdo_threads:
            t.join()

        for t in app_threads:
            t.join()

        logger.info('node has ended')

    def stop(self):
        '''End the run loop'''

        logger.info('stopping node')
        self.event.set()

    @property
    def od(self):
        '''For convenience. Access to the object dictionary.'''

        return self.node.object_dictionary
