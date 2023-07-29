import json
import zlib
from os import remove, listdir
from os.path import basename, isfile
from pathlib import Path
from enum import IntEnum, auto

from loguru import logger

from ...common.resource import Resource


class Subindex(IntEnum):
    FILE_NAME = auto()
    FILE_DATA = auto()
    CRC32 = auto()
    DELETE_FILE = auto()
    TOTAL_FILES = auto()
    FILE_NAMES = auto()


class FreadResource(Resource):
    '''Resource for readings file over the CAN bus'''

    def __init__(self):
        super().__init__()

        self.index = 0x3003
        self.file_path = ''

        self.tmp_dir = '/tmp/oresat/fread'
        Path(self.tmp_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f'fread tmp dir is {self.tmp_dir}')
        for i in listdir(self.tmp_dir):
            remove(f'{self.tmp_dir}/{i}')

    def on_start(self):

        self.node.add_sdo_read_callback(self.index, self.on_read)
        self.node.add_sdo_write_callback(self.index, self.on_write)

    def on_read(self, index: int, subindex: int):

        ret = None

        if index != self.index:
            return ret

        if subindex == Subindex.FILE_NAME:
            ret = basename(self.file_path)
        elif subindex == Subindex.FILE_DATA:
            if not self.file_path:
                logger.debug('fread file path was not set before trying to read file data')
                return b''

            try:
                with open(self.file_path, 'rb') as f:
                    ret = f.read()
            except FileNotFoundError as e:
                logger.exception(e)
        elif subindex == Subindex.CRC32:
            if isfile(self.file_path):
                with open(self.file_path, 'rb') as f:
                    ret = zlib.crc32(f.read())
            else:
                logger.debug(f'cannot get CRC32, file "{self.file_path}" does not exist')
                ret = 0
        elif subindex == Subindex.TOTAL_FILES:
            ret = len(self.node.fread_cache)
        elif subindex == Subindex.FILE_NAMES:
            ret = json.dumps([i.name for i in self.node.fread_cache.files()])

        return ret

    def on_write(self, index: int, subindex: int, value):

        if index != self.index:
            return

        if subindex == Subindex.FILE_NAME:
            try:
                self.file_path = self.node.fread_cache.get(value, self.tmp_dir, True)
            except FileNotFoundError:
                logger.error(f'file {value} not in fread cache')
                self.file_path = ''
        elif subindex == Subindex.DELETE_FILE:
            if self.file_path:
                # delete file from cache and tmp dir
                self.node.fread_cache.remove(basename(self.file_path))
                remove(self.file_path)
                self.file_path = ''
                logger.info(f'{basename(self.file_path)} was deleted from fread cache')
            else:
                logger.error('fread file path was not set before trying to delete file')
