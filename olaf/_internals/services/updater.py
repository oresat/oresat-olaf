"""Service for interacting with the updater"""

import canopen
from loguru import logger

from ...common.service import Service
from ..updater import Updater, UpdaterError


class UpdaterService(Service):
    """Service for interacting with the updater"""

    def __init__(self, updater: Updater):
        super().__init__()

        self._updater = updater
        self.update_obj: canopen.objectdictionary.Variable = None
        self.make_status_obj: canopen.objectdictionary.Variable = None

    def on_start(self):
        record = self.node.od["updater"]
        self.update_obj = record["update"]
        self.make_status_obj = record["make_status_file"]

        # make sure defaults are set correctly
        self.update_obj.value = False
        self.make_status_obj.value = False

        self.node.add_sdo_callbacks("updater", "status", self.on_read_status, None)
        self.node.add_sdo_callbacks("updater", "cache_files_json", self.on_read_cache_json, None)
        self.node.add_sdo_callbacks("updater", "cache_length", self.on_read_cache_len, None)

    def on_loop(self):
        # check for update files in fwrite cache
        for i in self.node.fwrite_cache.files("update"):
            self._updater.add_update_archive(self.node.fwrite_cache.dir + "/" + i)

        # check for flag to start a update
        if self.update_obj.value:
            try:
                self._updater.update()
            except UpdaterError as e:
                logger.exception(e)
            self.update_obj.value = False

        # check for flag to make a status archive
        if self.make_status_obj.value:
            status_archive_file_path = self._updater.make_status_archive()
            self.node.fread_cache.add(status_archive_file_path, consume=True)
            self.make_status_obj.value = False

        self.sleep(0.1)

    def on_read_status(self) -> int:
        """SDO read callback to get the status of update"""
        return self._updater.status.value

    def on_read_cache_len(self) -> int:
        """SDO read callback to get the number of updates cached"""
        return len(self._updater.updates_cached)

    def on_read_cache_json(self) -> str:
        """SDO read callback to get list of updates cached as str"""
        return " ".join(self._updater.updates_cached)
