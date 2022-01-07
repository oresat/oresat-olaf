
import canopen

from ..common.app import App
from ..updater import Updater
from ..common.oresat_file_cache import OreSatFileCache


class UpdaterApp(App):

    def __init__(self,
                 node: canopen.LocalNode,
                 fread_cache: OreSatFileCache,
                 fwrite_cache: OreSatFileCache,
                 work_dir: str,
                 cache_dir: str):

        super().__init__('Updater', 1.0)

        self.index = 0x3100
        self.subindex_status = 0x1
        self.subindex_updates_cached = 0x2
        self.subindex_list_available = 0x3
        self.subindex_update = 0x4
        self.subindex_make_statue_file = 0x5
        self.obj = node.object_dictionary[self.index]

        self._updater = Updater(work_dir, cache_dir)
        self._fread_cache = fread_cache
        self._fwrite_cache = fwrite_cache

        # make sure defaults are set
        self.obj[self.subindex_update].value = False
        self.obj[self.subindex_update].value = False
        self.obj[self.subindex_status].value = self._updater.status.value

        node.add_read_callback(self.on_read)

    def on_loop(self):

        for i in self._fwrite_cache.files('update'):
            self._updater.add_update(self._fwrite_cache.dir + '/' + i)

        if self.obj[self.subindex_update].value:
            self._updater.update()
            self.obj[self.subindex_update].value = False

        if self.obj[self.subindex_make_statue_file].value:
            status_archive_file_path = self.updater.make_status_archive()
            self._fread_cache.add(status_archive_file_path, consume=True)
            self.obj[self.subindex_make_statue_file].value = False

    def on_read(self, index: int, subindex: int, od: canopen.LocalNode):

        ret = None

        if index == self.index:
            if subindex == self.subindex_status:
                ret = self._updater.status.value
            elif subindex == self.subindex_updates_cached:
                ret = self._updater.updates_cached
            elif subindex == self.subindex_list_available:
                ret = ' '.join(self._cache.files())

        return ret
