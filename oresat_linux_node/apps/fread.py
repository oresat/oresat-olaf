
from os.path import basename

import canopen

from ..common.app import App
from ..common.oresat_file_cache import OreSatFileCache


class FreadApp(App):

    def __init__(self,
                 node: canopen.LocalNode,
                 fread_cache: OreSatFileCache,
                 tmp_dir: str = '/tmp/fread'):

        super().__init__('Fread', -1.0)

        self.fread_cache = fread_cache
        self.tmp_dir = tmp_dir

        self.index = 0x3003
        self.subindex_file_name = 0x1
        self.subindex_file_data = 0x2
        self.subindex_delete_file = 0x3

        self.file_path = ''

        node.add_read_callback(self.on_read)
        node.add_write_callback(self.on_write)

    def on_read(self, index: int, subindex: int, od: canopen.ObjectDictionary) -> bytes:

        ret = None

        if index != self.index or not self.fread_file:
            return

        if subindex == 0x1:  # file name
            ret = basename(self.file_path)
        elif subindex == 0x2:  # file data
            try:
                with open(self.file_path, 'rb') as f:
                    ret = f.read()
            except FileNotFoundError:
                pass

        return ret

    def on_write(self, index: int, subindex: int, od: canopen.ObjectDictionary, data: bytes):

        if index != self.index:
            return

        if subindex == self.subindex_file_name:
            file_name = data.decode()
            self.file_path = self.fread_cache.get(file_name, self.tmp_dir)
        elif subindex == self.subindex_delete_file and self.file_path:
            self.fwrite_cache.remove(basename(self.file_path))
