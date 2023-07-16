import struct
import subprocess
from enum import IntEnum
from os import geteuid
from pathlib import Path
from threading import Event

import canopen
import psutil
from loguru import logger

from ..common.daemon import Daemon
from ..common.timer_loop import TimerLoop
from ..common.oresat_file_cache import OreSatFileCache


class NodeStop(IntEnum):

    SOFT_RESET = 1
    '''Just stop the app and exit. Systemd will restart the app.'''
    HARD_RESET = 2
    '''Reboot system after app has stopped'''
    FACTORY_RESET = 3
    '''Clear all file cachces and reboot system after app has stopped'''
    POWER_OFF = 4
    '''Just power off the system.'''


class NetworkError(Exception):
    '''Error with the CANopen network / bus'''


class Node:
    '''OreSat CANopen Node'''

    def __init__(self, od: canopen.ObjectDictionary, bus: str):
        '''
        Parameters
        ----------
        od: canopen.ObjectDictionary
            The CANopen ObjectDictionary
        bus: str
            Which CAN bus to use.
        '''

        self._od = od
        self._bus = bus
        self._node = None
        self._network = None
        self._event = Event()
        self._read_cbs = {}
        self._write_cbs = {}
        self._syncs = 0
        self._reset = NodeStop.SOFT_RESET
        self._tpdo_timers = []
        self._daemons = {}

        if geteuid() == 0:  # running as root
            self.work_base_dir = '/var/lib/oresat'
            self.cache_base_dir = '/var/cache/oresat'
        else:
            self.work_base_dir = str(Path.home()) + '/.oresat'
            self.cache_base_dir = str(Path.home()) + '/.cache/oresat'

        fread_path = self.cache_base_dir + '/fread'
        fwrite_path = self.cache_base_dir + '/fwrite'

        self._fread_cache = OreSatFileCache(fread_path)
        self._fwrite_cache = OreSatFileCache(fwrite_path)

        logger.debug(f'fread cache path {self._fread_cache.dir}')
        logger.debug(f'fwrite cache path {self._fwrite_cache.dir}')

        # python canopen does not set the value to default for some reason
        for i in self.od:
            if not isinstance(self.od[i], canopen.objectdictionary.Variable):
                for j in self.od[i]:
                    if self.od[i][j].data_type == canopen.objectdictionary.BOOLEAN:
                        # fix bools to be bools
                        self.od[i][j].default = bool(self.od[i][j].default)
                        self.od[i][j].value = bool(self.od[i][j].default)
                    else:
                        self.od[i][j].value = self.od[i][j].default
            elif self.od[i].data_type == canopen.objectdictionary.BOOLEAN:
                # fix bools to be bools
                self.od[i].default = bool(self.od[i].default)
                self.od[i].value = bool(self.od[i].default)
            else:
                self.od[i].value = self.od[i].default

    def __del__(self):

        # stop the monitor thread if it is running
        if not self._event.is_set():
            self.stop()

        # stop the CANopen network
        if self._network:
            try:
                self._network.disconnect()
            except Exception:
                pass

    def _on_sync(self, cob_id: int, data: bytes, timestamp: float):
        '''On SYNC message send TPDOs configured to be SYNC-based'''

        self._syncs += 1
        if self._syncs == 241:
            self._syncs = 1

        for i in range(len(self._node.tpdo)):
            transmission_type = self.od[0x1800 + i][2].value
            if self._syncs % transmission_type == 0:
                self.send_tpdo(i)

    def send_tpdo(self, tpdo: int):
        '''
        Send a TPDO. Will not be sent if not node is not in operational state.

        Parameters
        ----------
        tpdo: int
            TPDO number to send

        Raises
        ------
        NetworkError
            Cannot send a TPDO message when the network is down.
        '''

        if self._network is None:
            raise NetworkError('network is down cannot send an TPDO message')

        # PDOs can't be sent if CAN bus is down and PDOs should not be sent if CAN bus not in
        # 'OPERATIONAL' state
        can_bus = psutil.net_if_stats().get(self._bus)
        if can_bus is None or (can_bus.isup and self._node.nmt.state != 'OPERATIONAL'):
            return True

        cob_id = self.od[0x1800 + tpdo][1].value & 0x3F_FF_FF_FF
        maps = self.od[0x1A00 + tpdo][0].value

        data = b''
        for i in range(maps):
            pdo_map = self.od[0x1A00 + tpdo][i + 1].value

            if pdo_map == 0:
                break  # nothing todo

            pdo_map_bytes = pdo_map.to_bytes(4, 'big')
            index, subindex, length = struct.unpack('>HBB', pdo_map_bytes)

            # call sdo callback(s) and convert data to bytes
            if isinstance(self.od[index], canopen.objectdictionary.Variable):
                value = self._node.sdo[index].phys
                value_bytes = self.od[index].encode_raw(value)
            else:  # record or array
                value = self._node.sdo[index][subindex].phys
                value_bytes = self.od[index][subindex].encode_raw(value)

            # pack pdo with bytes
            data += value_bytes

        try:
            i = self._network.send_message(cob_id, data)
        except Exception as e:
            logger.exception(f'TPDO{tpdo} failed with: {e}')

    def _tpdo_timer_loop(self, tpdo: int) -> bool:
        '''Send TPDO for TPDO loop. Can handle network errors.'''

        try:
            self.send_tpdo(tpdo)
        except NetworkError:
            pass

        return True

    def _on_rpdo_update_od(self, map: canopen.pdo.base.Map):
        '''Handle parsering an RPDO'''

        for i in map.map_array:
            if i == 0:
                continue

            value = map.map_array[i].raw
            if value == 0:
                break  # no more mapping

            index, subindex, size = struct.unpack('>HBB', value.to_bytes(4, 'big'))
            if isinstance(self.od[index], canopen.objectdictionary.Variable):
                self._node.sdo[index].raw = map.map[i - 1].get_data()
            else:
                self._node.sdo[index][subindex].raw = map.map[i - 1].get_data()

    def _setup_node(self):
        '''Create the CANopen and TPDO timer loops'''

        if self._od.node_id is None:
            self._od.node_id = 0x7C

        self._node = canopen.LocalNode(self._od.node_id, self._od)

        node_id = self._od.node_id
        default_rpdos = [0x200 + node_id, 0x300 + node_id, 0x400 + node_id, 0x500 + node_id]
        default_tpdos = [0x180 + node_id, 0x280 + node_id, 0x380 + node_id, 0x480 + node_id]

        # fix COB-IDs for invaild PDOs
        #
        # all oresat node RPDO COB-ID follow values of 0x[2345]00 + $NODEID
        # all oresat node TPDO COB-ID follow values of 0x[1234]80 + $NODEID
        # this fixes the values for all 16 RPDOs/TPDOs
        for i in range(len(self._node.rpdo)):
            cob_id = self.od[0x1400 + i][1].default & 0xFFF
            if cob_id in default_rpdos:
                cob_id = 0x200 + 0x100 * (i % 4) + node_id + i // 4
            else:
                cob_id = self.od[0x1400 + i][1].default
            self.od[0x1400 + i][1].value = cob_id
        for i in range(len(self._node.tpdo)):
            cob_id = self.od[0x1800 + i][1].default & 0xFFF
            if cob_id in default_tpdos:
                cob_id = 0x180 + 0x100 * (i % 4) + node_id + i // 4
            else:
                cob_id = self.od[0x1800 + i][1].default
            self.od[0x1800 + i][1].value = cob_id

        self._node.add_read_callback(self._on_sdo_read)
        self._node.add_write_callback(self._on_sdo_write)

        for i in range(len(self._node.tpdo)):
            transmission_type = self.od[0x1800 + i][2].default
            event_time = self.od[0x1800 + i][5].default
            if transmission_type in [0xFE, 0xFF] and event_time > 0:
                t = TimerLoop(name=f'TPDO{i + 1}', loop_func=self._tpdo_timer_loop,
                              delay=self.od[0x1800 + i][5], start_delay=self.od[0x1800 + i][3],
                              args=(i,))
                self._tpdo_timers.append(t)
                t.start()

    def _destroy_node(self):
        '''Destroy the CANopen and TPDO timer loops'''

        for t in self._tpdo_timers:
            t.stop()

        self._tpdo_timers = []  # remove all

        self._node = None

    def _restart_bus(self):
        '''Try to restart the CAN bus'''

        if self.first_bus_reset:
            logger.error(f'{self._bus} is down')

        if geteuid() == 0:  # running as root
            if self.first_bus_reset:
                logger.info(f'trying to restart CAN bus {self._bus}')
            cmd = (f'ip link set {self._bus} down;'
                   f'ip link set {self._bus} type can bitrate 1000000;'
                   f'ip link set {self._bus} up')
            out = subprocess.run(cmd, shell=True)
            if out.returncode != 0:
                logger.error(out)

        self.first_bus_reset = False

    def _restart_network(self):
        '''Restart the CANopen network'''

        logger.info('(re)starting CANopen network')

        self._network = canopen.Network()
        self._network.connect(bustype='socketcan', channel=self._bus)
        self._setup_node()
        self._network.add_node(self._node)

        try:
            self._node.nmt.start_heartbeat(self.od[0x1017].default)
            self._node.nmt.state = 'OPERATIONAL'
        except Exception as e:
            logger.exception(f'failed to (re)start CANopen network with {e}')

        self._network.subscribe(0x80, self._on_sync)

        # setup RPDOs callbacks
        self._node.rpdo.read()
        for i in self._node.rpdo:
            if self._node.rpdo[i].enabled:
                self._node.rpdo[i].add_callback(self._on_rpdo_update_od)

    def _disable_network(self):
        '''Disable the CANopen network'''

        try:
            if self._network:
                self._network.disconnect()
            self._destroy_node()
        except Exception:
            self._network = None  # make sure the canopen network is down
            self._node = None

    def _monitor_can(self):
        '''Monitor the CAN bus and CAN network'''

        first_bus_down = True  # flag to only log error message on first error
        self.first_bus_reset = True  # flag to only log error message on first error
        while not self._event.is_set():
            bus = psutil.net_if_stats().get(self._bus)
            if not bus:  # bus does not exist
                self._disable_network()
                if first_bus_down:
                    logger.critical(f'{self._bus} does not exists, nothing OLAF can do')
                    first_bus_down = False
            elif not bus.isup:  # bus is down
                first_bus_down = True  # reset flag
                self._disable_network()
                self._restart_bus()
            elif not self._network:  # bus is up, network is down
                first_bus_down = True  # reset flag
                self._restart_network()
            else:  # bus is up, network is up
                self.first_bus_reset = True  # reset flag
                first_bus_down = True  # reset flag

            self._event.wait(1)

    def run(self) -> int:
        '''
        Go into operational mode, start all the resources, start all the threads, and monitor
        everything in a loop.

        Returns
        -------
        NodeStop
            Reset / power off condition.
        '''

        logger.info(f'{self.name} node is starting')
        if geteuid() != 0:  # running as root
            logger.warning('not running as root, cannot restart CAN bus if it goes down')

        try:
            self._monitor_can()
        except Exception as e:
            logger.exception(e)

        # stop the node and TPDO timers
        self._destroy_node()

        logger.info(f'{self.name} node has ended')
        return self._reset

    def stop(self, reset: NodeStop = None):
        '''End the run loop'''

        if reset is not None:
            self._reset = reset
        self._event.set()

    def add_daemon(self, name: str):
        '''Add a daemon for the node to monitor and/or control'''

        self._daemons[name] = Daemon(name)

    def add_sdo_read_callback(self, index: int, sdo_cb):
        '''
        Add an SDO read callback

        Parameters
        ----------
        index: int
            The index to call the callback on.
        sdo_cb
            The SDO read callback. Must take index and subindex args and return a valid value or
            None to use the value from the OD.
        '''

        if index not in self._read_cbs:
            self._read_cbs[index] = [sdo_cb]
        else:
            self._read_cbs[index].append(sdo_cb)

    def add_sdo_write_callback(self, index: int, sdo_cb):
        '''
        Add an SDO write callback

        Parameters
        ----------
        index: int
            The index to call the callback on.
        sdo_cb
            The SDO read callback. Must take index, subindex, value args.
        '''

        if index not in self._write_cbs:
            self._write_cbs[index] = [sdo_cb]
        else:
            self._write_cbs[index].append(sdo_cb)

    def send_emcy(self, code: int, register: int = 0, data: bytes = b''):
        '''
        Send a EMCY message. Wrapper on canopen's `EmcyProducer.send`.

        Parameters
        ----------
        code: int
            The EMCY code.
        register: int
            Optional error register value in EMCY message (uint8). See Object 1001 def for bit
            field.
        manufacturer_code: bytes
            Optional manufacturer error code (up to 5 bytes).

        Raises
        ------
        NetworkError
            Cannot send a EMCY message when the network is down.
        '''

        if self._network is None:
            raise NetworkError('network is down cannot send an EMCY message')

        self._node.emcy.send(code, register, data)

    def _on_sdo_read(self, index: int, subindex: int, od: canopen.objectdictionary.Variable):
        '''
        SDO read callback function. Allows overriding the data being sent on a SDO read. Return
        valid datatype for object, if overriding read data, or :py:data:`None` to use the the value
        on object dictionary.

        Parameters
        ----------
        index: int
            The index the SDO is reading to.
        subindex: int
            The subindex the SDO is reading to.
        od: canopen.objectdictionary.Variable
            The variable object being read to. Badly named.

        Returns
        -------
        Any
            The value to return for that index / subindex. Return :py:data:`None` if invalid index
            / subindex.
        '''

        ret = None

        if index in self._read_cbs:
            for cb_func in self._read_cbs[index]:
                try:
                    ret = cb_func(index, subindex)
                except Exception as e:
                    logger.exception(f'sdo read cb for 0x{index:04X} 0x{subindex:02X} raised: {e}')

        # get value from OD
        if ret is None:
            ret = od.value

        return ret

    def _on_sdo_write(self, index: int, subindex: int, od: canopen.objectdictionary.Variable,
                      data: bytes):
        '''
        SDO write callback function. Gives access to the data being received on a SDO write.

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

        # set value in OD before callback
        od.value = od.decode_raw(data)

        if index in self._write_cbs:
            value = od.decode_raw(data)
            for cb_func in self._write_cbs[index]:
                try:
                    cb_func(index, subindex, value)
                except Exception as e:
                    logger.exception(f'sdo write cb for 0x{index:04X} 0x{subindex:02X} raised: '
                                     f'{e}')

    @property
    def name(self) -> str:
        '''str: The nodes name.'''

        return self._od.device_information.product_name

    @property
    def od(self) -> canopen.ObjectDictionary:
        '''canopen.ObjectDictionary: Access to the object dictionary.'''

        return self._od

    @property
    def fread_cache(self) -> OreSatFileCache:
        '''OreSatFile: Cache the CANopen master node can read to.'''

        return self._fread_cache

    @property
    def fwrite_cache(self) -> OreSatFileCache:
        '''OreSatFile: Cache the CANopen master node can write to.'''

        return self._fwrite_cache

    @property
    def is_running(self) -> bool:
        '''bool: Is the node loop running'''

        return not self._event.is_set()

    @property
    def daemons(self) -> dict:
        '''dict: The dictionary of external daemons that are monitored and/or controllable'''

        return self._daemons
