import json
import zlib
from os import remove, listdir
from os.path import basename, isfile
from pathlib import Path
from enum import IntEnum, auto

from loguru import logger

from ...common.oresat_file import OreSatFile
from ...common.resource import Resource


class Subindex(IntEnum):
    FILE_NAME = auto()
    FILE_DATA = auto()
    CRC32 = auto()
    DELETE_FILE = auto()
    TOTAL_FILES = auto()
    FILE_NAMES = auto()


class FwriteResource(Resource):
    '''Resource for writing files over the CAN bus'''

    def __init__(self):
        super().__init__()

        self.index = 0x3004
        self.file_path = ''

        self.tmp_dir = '/tmp/oresat/fwrite'
        Path(self.tmp_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f'fwrite tmp dir is {self.tmp_dir}')
        for i in listdir(self.tmp_dir):
            remove(f'{self.tmp_dir}/{i}')

    def on_start(self):

        self.node.add_sdo_read_callback(self.index, self.on_read)
        self.node.add_sdo_write_callback(self.index, self.on_write)

    def on_read(self, index: int, subindex: int):

        ret = None

        if index != self.index:
            return

        if subindex == Subindex.FILE_NAME:
            ret = basename(self.file_path)
        elif subindex == Subindex.CRC32:
            if isfile(self.file_path):
                with open(self.file_path, 'rb') as f:
                    ret = zlib.crc32(f.read())
            else:
                logger.debug(f'cannot get CRC32, file "{self.file_path}" does not exist')
                ret = 0
        elif subindex == Subindex.TOTAL_FILES:
            ret = len(self.node.fwrite_cache)
        elif subindex == Subindex.FILE_NAMES:
            ret = json.dumps([i.name for i in self.node.fwrite_cache.files()])

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

            # clear file data OD obj value to not waste memory
            self.node.od[index][subindex].value = ''
        elif subindex == Subindex.DELETE_FILE:
            if self.file_path:
                # delete file from cache and tmp dir
                self.node.fwrite_cache.remove(basename(self.file_path))
                remove(self.file_path)
                self.file_path = ''
                logger.info(f'{basename(self.file_path)} was deleted from fwrite cache')
            else:
                logger.error('fwrite file path was not set before trying to delete file')
