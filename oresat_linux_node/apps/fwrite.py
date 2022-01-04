
from os.path import basename

import canopen

from ..common.app import App
from ..common.oresat_file_cache import OreSatFileCache


class FwriteApp(App):

    def __init__(self,
                 node: canopen.LocalNode,
                 fwrite_cache: OreSatFileCache,
                 tmp_dir: str = '/tmp/fwrite'):

        super().__init__('Fwrite', -1.0)

        self.node = node
        self.fwrite_cache = fwrite_cache
        self.tmp_dir = tmp_dir

        self.index = 0x3004
        self.subindex_file_name = 0x1
        self.subindex_file_data = 0x2

        self.file_path = ''

        self.node.add_read_callback(self.on_read)
        self.node.add_write_callback(self.on_write)

    def on_read(self, index: int, subindex: int, od: canopen.ObjectDictionary) -> bytes:

        ret = None

        if index == self.index and self.file_path and subindex == self.subindex_file_name:
            ret = basename(self._file_path)

        return ret

    def on_write(self, index: int, subindex: int, od: canopen.ObjectDictionary, data: bytes):

        if index != self.index:
            return

        if subindex == self.subindex_file_name:
            file_name = data.decode()
            self.file_path = self.fwrite_cache.get(file_name, self.tmp_dir)
        elif subindex == self.subindex_file_data and self.file_path:
            try:
                with open(self.file_path, 'wb') as f:
                    f.write(data)
            except FileNotFoundError:
                pass

            self.file_path = ''

            # clear buffers to not was memory
            od[index][subindex].value = ''
            self.node.sdo[index][subindex].value = ''
