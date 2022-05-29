from os import remove, listdir
from os.path import basename
from pathlib import Path
from enum import IntEnum, auto

import canopen
from loguru import logger

from ..common.resource import Resource
from ..common.oresat_file_cache import OreSatFileCache


class Subindex(IntEnum):
    FILE_NAME = auto()
    FILE_DATA = auto()


class FwriteResource(Resource):
    '''Resource for writing files over the CAN bus'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tmp_dir = '/tmp/oresat/fwrite'
        Path(self.tmp_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f'fread tmp dir is {self.tmp_dir}')
        for i in listdir(self.tmp_dir):
            remove(f'{self.tmp_dir}/{i}')

        self.index = 0x3004

        self.file_path = ''

    def on_read(self, index, subindex, od):

        ret = None

        if index == self.index and self.file_path and subindex == Subindex.FILE_NAME:
            ret = basename(self._file_path)

        return ret

    def on_write(self, index, subindex, od, data):

        if index != self.index:
            return

        if subindex == Subindex.FILE_NAME:
            file_name = data.decode()
            self.file_path = self.tmp_dir + '/' + file_name
        elif subindex == Subindex.FILE_DATA:
            if not self.file_path:
                logger.error('fwrite file path was not set before file data was sent')
                return

            try:
                with open(self.file_path, 'wb') as f:
                    f.write(data)
                logger.info(self.name + ' receive new file: ' + basename(self.file_path))
                self.fwrite_cache.add(self.file_path, consume=True)
            except FileNotFoundError as exc:
                logger.error(exc)

            self.file_path = ''

            # clear buffers to not waste memory
            self.od[index][subindex].value = ''
