
import canopen

from ..common.app import App
from ..common.oresat_file_cache import OreSatFileCache


class FileCacheApp(App):

    def __init__(self,
                 node: canopen.LocalNode,
                 file_cache: OreSatFileCache,
                 index: int,
                 name: str = 'File Cache'):

        super().__init__(name, -1.0)

        self.file_cache = file_cache
        self.iter = 0
        self.filter = ''

        self.index = index
        self.subindex_cache_dir = 0x1
        self.subindex_total_files = 0x2
        self.subindex_filter = 0x3
        self.subindex_files = 0x4
        self.subindex_iter = 0x5
        self.subindex_file_name = 0x6
        self.subindex_file_size = 0x7
        self.subindex_file_crc32 = 0x8
        self.subindex_delete_file = 0x9

        node.add_read_callback(self.on_read)
        node.add_write_callback(self.on_write)

    def on_read(self, index: int, subindex: int, od: canopen.ObjectDictionary) -> bytes:
        '''On SDO read to file cache object'''

        ret = None

        if index != self.index:
            return ret

        if subindex == self.subindex_cache_dir:
            ret = self.file_cache.dir
        elif subindex == self.subindex_total_files:
            ret = len(self.file_cache)
        elif subindex == self.subindex_filter:
            ret = self.filter
        elif subindex == self.subindex_files:
            ret = len(self.file_cache.files(self.filter))
        elif subindex == self.subindex_iter:
            ret = self.iter
        elif subindex == self.subindex_file_name:
            ret = self.file_cache.files(self.filter)[self.iter].name
        elif subindex == self.subindex_file_size:
            ret = self.file_cache.files(self.filter)[self.iter].size
        elif subindex == self.subindex_file_crc32:
            ret = self.file_cache.files(self.filter)[self.iter].crc32

        return ret

    def on_write(self, index: int, subindex: int, od: canopen.ObjectDictionary, data: bytes):
        '''On SDO write to file cache object'''

        if index != self.index:
            return

        if subindex == self.subindex_filter:
            if not data or not data.decode():  # empty or NULL terminator
                self.filter = ''
            else:
                data.decode()
        elif subindex == self.subindex_iter:
            self.iter = od[index][subindex].decode(data)
        elif subindex == self.subindex_delete_file:
            file_name = self.file_cache.files(self.filter)[self.iter].name
            self.file_cache.remove(file_name)
