import canopen
from loguru import logger

from ..common.resource import Resource
from ..common.oresat_file_cache import OreSatFileCache
from ..updater import Updater, UpdaterError


class UpdaterResource(Resource):
    '''Resource for interacting with the updater'''

    index = 0x3100
    sub_status = 0x1
    sub_updates_cached = 0x2
    sub_list_available = 0x3
    sub_update = 0x4

    def __init__(self,
                 node: canopen.LocalNode,
                 fread_cache: OreSatFileCache,
                 fwrite_cache: OreSatFileCache,
                 work_dir: str,
                 cache_dir: str):

        super().__init__(node, 'Updater', 1.0)

        self.sub_make_statue_file = 0x5
        self.obj = node.object_dictionary[self.index]

        self._updater = Updater(work_dir, cache_dir)
        self._fread_cache = fread_cache
        self._fwrite_cache = fwrite_cache

        # make sure defaults are set
        self.obj[self.sub_update].value = False
        self.obj[self.sub_update].value = False

        node.add_read_callback(self.on_read)

    def on_loop(self):

        for i in self._fwrite_cache.files('update'):
            self._updater.add_update(self._fwrite_cache.dir + '/' + i)

        if self.obj[self.sub_update].value:
            try:
                self._updater.update()
            except UpdaterError as exc:
                logger.error(exc)
            self.obj[self.sub_update].value = False

        if self.obj[self.sub_make_statue_file].value:
            status_archive_file_path = self.updater.make_status_archive()
            self._fread_cache.add(status_archive_file_path, consume=True)
            self.obj[self.sub_make_statue_file].value = False

    def on_read(self, index, subindex, od):

        ret = None

        if index == self.index:
            if subindex == self.sub_status:
                ret = self._updater.status.value
            elif subindex == self.sub_updates_cached:
                ret = self._updater.updates_cached
            elif subindex == self.sub_list_available:
                ret = ' '.join(self._cache.files())

        return ret
