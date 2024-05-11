"""Service for interacting with the updater"""

from loguru import logger

from ...common.service import Service
from ..updater import Updater, UpdaterError


class UpdaterService(Service):
    """Service for interacting with the updater"""

    def __init__(self, updater: Updater):
        super().__init__()
        self._updater = updater

    def on_start(self):

        # make sure defaults are set correctly
        self.node.od_write("updater", "update", False)
        self.node.od_write("updater", "make_status_file", False)

        self.node.add_sdo_callbacks("updater", "status", self.on_read_status, None)
        self.node.add_sdo_callbacks("updater", "cache_files_json", self.on_read_cache_json, None)
        self.node.add_sdo_callbacks("updater", "cache_length", self.on_read_cache_len, None)

    def on_loop(self):
        # check for update files in fwrite cache
        for i in self.node.fwrite_cache.files("update"):
            self._updater.add_update_archive(self.node.fwrite_cache.dir + "/" + i.name)
            self.node.fwrite_cache.remove(i.name)
            logger.info(f"updater moved {i.name} into update cache")

        # check for flag to start a update
        if self.node.od_read("updater", "update"):
            try:
                self._updater.update()
            except UpdaterError as e:
                logger.exception(e)
            self.node.od_write("updater", "update", False)

        # check for flag to make a status archive
        if self.node.od_read("updater", "make_status_file"):
            status_archive_file_path = self._updater.make_status_archive()
            self.node.fread_cache.add(status_archive_file_path, consume=True)
            self.node.od_write("updater", "make_status_file", False)

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
