"""Service for interacting with the updater"""

import os
from os.path import abspath

from loguru import logger

from time import monotonic

from ...common.service import Service
from ...common.oresat_file import OreSatFile
from ..updater import Updater, UpdaterError
from ...canopen.master_node import MasterNode


class UpdaterService(Service):
    """Service for interacting with the updater"""

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
        self.check_for_updates()

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

        if self.node.od_db[i.card_underscore][0x3002][0x4].name != "sw_version":
            logger.warning(f"Update archive is for {i.card_underscore}, which is not OLAF.")
            return

        if (
            self.node.node_status[i.card_underscore][0] != 0x05
            or self.node.node_status[i.card_underscore][2] + self.INACTIVE_TIMEOUT < monotonic()
        ):
            logger.warning(f"Update archive is for {i.card_underscore}, which is not on.")
            return

        # get the file data
        path = abspath(self.node.fwrite_cache.dir + "/" + i.name)
        with open(path, "rb") as f:
            data = f.read()

        # transfer the file
        logger.info(f"Sending {i.name} to remote node {remote_node_id}")
        self.node.sdo_write(i.card_underscore, "fwrite_cache", "file_name", i.name)
        self.node.sdo_write(i.card_underscore, "fwrite_cache", "file_data", data)

        # delete the update file
        self.node.fwrite_cache.remove(i.name)

    def check_for_updates(self, value: bool = True) -> None:
        """Check for updates in the fwrite cache. Send updates to other cards if they are on"""
        for i in self.node.fwrite_cache.files("update"):
            if i.card == self._hostname:
                self._updater.add_update_archive(self.node.fwrite_cache.dir + "/" + i.name)
                self.node.fwrite_cache.remove(i.name)
                logger.info(f"updater moved {i.name} into update cache")

            elif isinstance(self.node, MasterNode):
                self.send_update(i)
