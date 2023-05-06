from os import remove, listdir
from os.path import basename
from pathlib import Path
from enum import IntEnum, auto

from loguru import logger

from ...common.oresat_file import OreSatFile
from ...common.resource import Resource


class Subindex(IntEnum):
    FILE_NAME = auto()
    FILE_DATA = auto()


class FwriteResource(Resource):
    '''Resource for writing files over the CAN bus'''

    def __init__(self):
        super().__init__()

        self.index = 0x3004
        self.file_path = ''

        self.tmp_dir = '/tmp/oresat/fwrite'
        Path(self.tmp_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f'fread tmp dir is {self.tmp_dir}')
        for i in listdir(self.tmp_dir):
            remove(f'{self.tmp_dir}/{i}')

    def on_start(self):

        self.node.add_sdo_read_callback(self.index, self.on_read)
        self.node.add_sdo_write_callback(self.index, self.on_write)

    def on_read(self, index: int, subindex: int):

        ret = None

        if index == self.index and subindex == Subindex.FILE_NAME:
            ret = basename(self.file_path)

        return ret

    def on_write(self, index: int, subindex: int, value):

        if index != self.index:
            return

        if subindex == Subindex.FILE_NAME:
            try:
                OreSatFile(value)  # valiate file name format
                self.file_path = self.tmp_dir + '/' + value
            except ValueError:
                logger.error(f'{value} is not a valid file name format')
                self.file_path = ''

        elif subindex == Subindex.FILE_DATA:
            if not self.file_path:
                logger.error('fwrite file path was not set before file data was sent')
                return

            try:
                with open(self.file_path, 'wb') as f:
                    f.write(value)
                logger.info(f'receive new file: {basename(self.file_path)}')
                self.node.fwrite_cache.add(self.file_path, consume=True)
            except Exception as e:
                logger.exception(e)

            self.file_path = ''

            # clear buffers to not waste memory
            self.node.od[index][subindex].value = ''
