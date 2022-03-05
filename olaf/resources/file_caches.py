import canopen
from loguru import logger

from ..common.resource import Resource
from ..common.oresat_file_cache import OreSatFileCache


class FileCachesResource(Resource):
    '''Resource for interacting with the fread and fwrite caches'''

    def __init__(self,
                 node: canopen.LocalNode,
                 fread_cache: OreSatFileCache,
                 fwrite_cache: OreSatFileCache,
                 name: str = 'File Caches'):

        super().__init__(node, name, -1.0)

        self.fread_cache = fread_cache
        self.fwrite_cache = fwrite_cache
        self.file_caches = [self.fread_cache, self.fwrite_cache]
        self.selector = 0
        self.iter = 0
        self.filter = ''

        self.index = 0x3002
        self.sub_fread_len = 0x1
        self.sub_fwrite_len = 0x2
        self.sub_cache_selector = 0x3
        self.sub_filter = 0x4
        self.sub_cache_len = 0x5
        self.sub_iter = 0x6
        self.sub_file_name = 0x7
        self.sub_file_size = 0x8
        self.sub_delete_file = 0x9

    def on_read(self, index, subindex, od):

        ret = None

        if index != self.index:
            return ret

        try:
            if subindex == self.sub_fread_len:
                ret = len(self.fread_cache)
            elif subindex == self.sub_fwrite_len:
                ret = len(self.fwrite_cache)
            elif subindex == self.sub_filter:
                ret = self.filter
            elif subindex == self.sub_cache_len:
                ret = len(self.file_caches[self.selector].files(self.filter))
            elif subindex == self.sub_iter:
                ret = self.iter
            elif subindex == self.sub_file_name:
                ret = self.file_caches[self.selector].files(self.filter)[self.iter].name
            elif subindex == self.sub_file_size:
                ret = self.file_caches[self.selector].files(self.filter)[self.iter].size
        except Exception as exc:
            logger.error(exc)

        return ret

    def on_write(self, index, subindex, od, data):

        if index != self.index:
            return

        if subindex == self.sub_cache_selector:
            self.selector = self.node.object_dictionary[index][subindex].decode_raw(data)
        elif subindex == self.sub_filter:
            if not data or not data.decode():  # empty or NULL terminator
                self.filter = ''
            else:
                data.decode()
        elif subindex == self.sub_iter:
            self.iter = self.node.object_dictionary[index][subindex].decode_raw(data)
        elif subindex == self.sub_delete_file:
            file_name = self.file_caches[self.selector].files(self.filter)[self.iter].name
            self.file_cache.remove(file_name)
