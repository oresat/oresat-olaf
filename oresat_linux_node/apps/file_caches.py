import logging

import canopen

from ..common.app import App
from ..common.oresat_file_cache import OreSatFileCache


class FileCachesApp(App):

    def __init__(self,
                 node: canopen.LocalNode,
                 fread_cache: OreSatFileCache,
                 fwrite_cache: OreSatFileCache,
                 name: str = 'File Caches'):

        super().__init__(name, -1.0)

        self.node = node
        self.fread_cache = fread_cache
        self.fwrite_cache = fwrite_cache
        self.file_caches = [self.fread_cache, self.fwrite_cache]
        self.selector = 0
        self.iter = 0
        self.filter = ''

        self.index = 0x3002
        self.subindex_fread_len = 0x1
        self.subindex_fwrite_len = 0x2
        self.subindex_cache_selector = 0x3
        self.subindex_filter = 0x4
        self.subindex_cache_len = 0x5
        self.subindex_iter = 0x6
        self.subindex_file_name = 0x7
        self.subindex_file_size = 0x8
        self.subindex_delete_file = 0x9

        node.add_read_callback(self.on_read)
        node.add_write_callback(self.on_write)

    def on_read(self, index: int, subindex: int, od: canopen.ObjectDictionary) -> bytes:
        '''On SDO read to file caches object'''

        ret = None

        if index != self.index:
            return ret

        try:
            if subindex == self.subindex_fread_len:
                ret = len(self.fread_cache)
            elif subindex == self.subindex_fwrite_len:
                ret = len(self.fwrite_cache)
            elif subindex == self.subindex_filter:
                ret = self.filter
            elif subindex == self.subindex_cache_len:
                ret = len(self.file_caches[self.selector].files(self.filter))
            elif subindex == self.subindex_iter:
                ret = self.iter
            elif subindex == self.subindex_file_name:
                ret = self.file_caches[self.selector].files(self.filter)[self.iter].name
            elif subindex == self.subindex_file_size:
                ret = self.file_caches[self.selector].files(self.filter)[self.iter].size
        except Exception as exc:
            logging.error(exc)

        return ret

    def on_write(self, index: int, subindex: int, od: canopen.ObjectDictionary, data: bytes):
        '''On SDO write to file caches object'''

        if index != self.index:
            return

        if subindex == self.subindex_cache_selector:
            self.selector = self.node.object_dictionary[index][subindex].decode_raw(data)
        elif subindex == self.subindex_filter:
            if not data or not data.decode():  # empty or NULL terminator
                self.filter = ''
            else:
                data.decode()
        elif subindex == self.subindex_iter:
            self.iter = self.node.object_dictionary[index][subindex].decode_raw(data)
        elif subindex == self.subindex_delete_file:
            file_name = self.file_caches[self.selector].files(self.filter)[self.iter].name
            self.file_cache.remove(file_name)
