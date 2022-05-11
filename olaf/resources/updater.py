from enum import IntEnum, auto

import canopen
from loguru import logger

from ..common.resource import Resource
from ..common.oresat_file_cache import OreSatFileCache
from ..updater import Updater, UpdaterError


class Subindex(IntEnum):
    STATUS = auto()
    UPDATES_CACHED = auto()
    LIST_AVAILABLE = auto()
    UPDATE = auto()
    MAKE_STATUS_FILE = auto()


class UpdaterResource(Resource):
    '''Resource for interacting with the updater'''

    index = 0x3100

    def __init__(self,
                 node: canopen.LocalNode,
                 fread_cache: OreSatFileCache,
                 fwrite_cache: OreSatFileCache,
                 work_dir: str,
                 cache_dir: str):

        super().__init__(node, 'Updater', 1.0)

        self._updater = Updater(work_dir, cache_dir)
        self._fread_cache = fread_cache
        self._fwrite_cache = fwrite_cache

        record = node.object_dictionary[self.index]
        self.update_obj = record[Subindex.UPDATE.value]
        self.make_status_obj = record[Subindex.MAKE_STATUS_FILE.value]

        # make sure defaults are set correctly (override the values from eds/dcf)
        self.update_obj.value = False
        self.make_status_obj.value = False

    def on_loop(self):

        for i in self._fwrite_cache.files('update'):
            self._updater.add_update(self._fwrite_cache.dir + '/' + i)

        if self.update_obj.value:
            try:
                self._updater.update()
            except UpdaterError as exc:
                logger.error(exc)
            self.update_obj.value = False

        if self.make_status_obj.value:
            status_archive_file_path = self._updater.make_status_archive()
            self._fread_cache.add(status_archive_file_path, consume=True)
            self.make_status_obj.value = False

    def on_read(self, index, subindex, od):

        ret = None

        if index == self.index:
            if subindex == Subindex.STATUS:
                ret = self._updater.status.value
            elif subindex == Subindex.UPDATES_CACHED:
                ret = self._updater.updates_cached
            elif subindex == Subindex.LIST_AVAILABLE:
                ret = ' '.join(self._cache.files())

        return ret
