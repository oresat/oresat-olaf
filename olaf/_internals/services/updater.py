from enum import IntEnum, auto

from loguru import logger

from ...common.service import Service
from ..updater import Updater, UpdaterError


class Subindex(IntEnum):
    STATUS = auto()
    UPDATES_CACHED = auto()
    LIST_AVAILABLE = auto()
    UPDATE = auto()
    MAKE_STATUS_FILE = auto()


class UpdaterService(Service):
    '''Service for interacting with the updater'''

    def __init__(self, updater: Updater):
        super().__init__()

        self._updater = updater
        self.index = 0x3100

    def on_start(self):

        record = self.node.od[self.index]
        self.update_obj = record[Subindex.UPDATE.value]
        self.make_status_obj = record[Subindex.MAKE_STATUS_FILE.value]

        # make sure defaults are set correctly (override the values from eds/dcf)
        self.update_obj.value = False
        self.make_status_obj.value = False

        self.node.add_sdo_read_callback(self.index, self.on_read)

    def on_loop(self):

        # check for update files in fwrite cache
        for i in self.node.fwrite_cache.files('update'):
            self._updater.add_update(self.node.fwrite_cache.dir + '/' + i)

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

        self.sleep(0.5)

    def on_read(self, index: int, subindex: int):

        ret = None

        if index == self.index:
            if subindex == Subindex.STATUS:
                ret = self._updater.status.value
            elif subindex == Subindex.UPDATES_CACHED:
                ret = len(self._updater.updates_cached)
            elif subindex == Subindex.LIST_AVAILABLE:
                ret = ' '.join(self._updater.updates_cached)

        return ret
