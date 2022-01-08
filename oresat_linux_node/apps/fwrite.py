
from os.path import basename
from pathlib import Path

import canopen
from loguru import logger

from ..common.app import App
from ..common.oresat_file_cache import OreSatFileCache


class FwriteApp(App):

    def __init__(self,
                 node: canopen.LocalNode,
                 fwrite_cache: OreSatFileCache,
                 tmp_dir: str = '/tmp/oresat-fwrite'):

        super().__init__('Fwrite', -1.0)

        self.node = node
        self.fwrite_cache = fwrite_cache
        self.tmp_dir = tmp_dir
        Path(self.tmp_dir).mkdir(parents=True, exist_ok=True)

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
            self.file_path = self.tmp_dir + '/' + file_name
        elif subindex == self.subindex_file_data:
            if not self.file_path:
                logger.error('fwrite file path was not set before file data was sent')
                return

            try:
                with open(self.file_path, 'wb') as f:
                    f.write(data)
                logger.info(self.name + ' receive new file: ' + file_name)
                self.fwrite_cache.add(self.file_path, consume=True)
            except FileNotFoundError as exc:
                logger.error(exc)

            self.file_path = ''

            # clear buffers to not was memory
            self.node.object_dictionary[index][subindex].value = ''
            self.node.sdo[index][subindex].value = ''
