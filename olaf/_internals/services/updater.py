"""Service for interacting with the updater"""

import os
from os.path import abspath
from time import monotonic

from canopen import SdoCommunicationError
from loguru import logger

from ...canopen.master_node import MasterNode
from ...common.oresat_file import OreSatFile
from ...common.service import Service
from ..updater import Updater, UpdaterError


class UpdaterService(Service):
    """Service for interacting with the updater"""

    INACTIVE_TIMEOUT = 5

    def __init__(self, updater: Updater) -> None:
        super().__init__()
        self._updater = updater
        self._hostname = os.uname()[1].removeprefix("oresat-")

    def on_start(self) -> None:
        # make sure defaults are set correctly
        self.node.od_write("updater", "update", value=False)
        self.node.od_write("updater", "make_status_file", value=False)

        self.node.add_sdo_callbacks("updater", "status", self.on_read_status, None)
        self.node.add_sdo_callbacks("updater", "cache_files_json", self.on_read_cache_json, None)
        self.node.add_sdo_callbacks("updater", "cache_length", self.on_read_cache_len, None)
        self.node.add_sdo_callbacks("updater", "check_for_updates", None, self.check_for_updates)

        # check for update files in fwrite cache
        self._check_local_updates()

    def on_loop(self) -> None:
        # check for flag to start a update
        if self.node.od_read("updater", "update"):
            try:
                self._updater.update()
            except UpdaterError as e:
                logger.exception(e)
            self.node.od_write("updater", "update", value=False)

        # check for flag to make a status archive
        if self.node.od_read("updater", "make_status_file"):
            status_archive_file_path = self._updater.make_status_archive()
            self.node.fread_cache.add(status_archive_file_path, consume=True)
            self.node.od_write("updater", "make_status_file", value=False)

        self.sleep(0.1)

    def on_read_status(self) -> int:
        """SDO read callback to get the status of update"""
        return self._updater.status.value

    def on_read_cache_len(self) -> int:
        """SDO read callback to get the number of updates cached"""
        return len(self._updater.updates_cached)

    def on_read_cache_json(self) -> str:
        """SDO read callback to get list of updates cached as str"""
        return " ".join([i.name for i in self._updater.updates_cached])

    def send_update(self, i: OreSatFile) -> None:
        try:
            remote_node_id = self.node.od_db[i.card_underscore].node_id
        except KeyError:
            logger.error(
                f"Could not find node for update {i.card_underscore} in object dictionary db"
            )
            return

        # Check if the target card is a software or firmware card. This update path only works
        # with software cards and the easiest way to tell from the object dictionary is to check
        # od["versions"][4] which will either be named "fw_version" or "sw_version"
        if self.node.od_db[i.card_underscore]['versions'][0x4].name != "sw_version":
            logger.warning(f"Update archive is for {i.card_underscore}, which is not OLAF.")
            return

        if i.card_underscore not in self.node.node_status:
            logger.warning(f"'{i.card_underscore}' not found in node_status, skipping")
            return

        heartbeat = self.node.node_status[i.card_underscore]
        # State 0x05 is "Operational" - see CANopen hearbeat spec
        if heartbeat.state != 0x05 or heartbeat.timestamp + self.INACTIVE_TIMEOUT < monotonic():
            logger.warning(f"Update archive is for {i.card_underscore}, which is not on.")
            return

        # get the file data
        path = abspath(self.node.fwrite_cache.dir + "/" + i.name)
        with open(path, "rb") as f:
            data = f.read()

        # transfer the file
        logger.info(f"Sending {i.name} to remote node {remote_node_id:#02x}")
        try:
            self.node.sdo_write(i.card_underscore, "fwrite_cache", "file_name", i.name)
            self.node.sdo_write(i.card_underscore, "fwrite_cache", "file_data", data)
        except SdoCommunicationError as e:
            logger.error(f"Failed writing {i.name} to {remote_node_id:#02x}: {e}")
            return

        # delete the update file
        self.node.fwrite_cache.remove(i.name)

    def _check_local_updates(self) -> None:
        """Check for updates in the fwrite cache."""
        logger.info("Checking for local updates")
        for file in self.node.fwrite_cache.files("update"):
            if file.card == self._hostname:
                self._updater.add_update_archive(self.node.fwrite_cache.dir + "/" + file.name)
                self.node.fwrite_cache.remove(file.name)
                logger.info(f"updater moved {file.name} into update cache")

    def _check_remote_updates(self) -> None:
        """Check the fwrite cache for files that should be distributed to other cards"""
        logger.info("Checking for remote updates")
        if isinstance(self.node, MasterNode):
            for file in self.node.fwrite_cache.files("update"):
                if file.card != self._hostname:
                    logger.info(f"Sending {file.name} to {file.card_underscore}")
                    self.send_update(file)

    def check_for_updates(self, value: bool = True) -> None:
        """Check for updates in the fwrite cache. Send updates to other cards if they are on"""
        self._check_remote_updates()
        self._check_local_updates()
