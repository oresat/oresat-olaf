import zlib
from os import remove, listdir
from os.path import basename
from pathlib import Path
from enum import IntEnum, auto

from loguru import logger

from ...common.resource import Resource


class Subindex(IntEnum):
    FILE_NAME = auto()
    FILE_DATA = auto()
    CRC32 = auto()
    DELETE_FILE = auto()


class FreadResource(Resource):
    '''Resource for readings file over the CAN bus'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tmp_dir = '/tmp/oresat/fread'
        Path(self.tmp_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f'fread tmp dir is {self.tmp_dir}')
        for i in listdir(self.tmp_dir):
            remove(f'{self.tmp_dir}/{i}')

        self.index = 0x3003

        self.file_path = ''

    def on_read(self, index, subindex, od):

        ret = None

        if index != self.index:
            return ret

        if subindex == Subindex.FILE_NAME:
            ret = basename(self.file_path)
        elif subindex == Subindex.CRC32:
            try:
                with open(self.file_path, 'rb') as f:
                    ret = zlib.crc32(f.read())
            except FileNotFoundError as exc:
                logger.error(exc)
        elif subindex == Subindex.FILE_DATA:
            if not self.file_path:
                logger.error('fread file path was not set before trying to read file data')
                return b''

            try:
                with open(self.file_path, 'rb') as f:
                    ret = f.read()
            except FileNotFoundError as exc:
                logger.error(exc)

        return ret

    def on_write(self, index, subindex, od, data):

        if index != self.index:
            return

        if subindex == Subindex.FILE_NAME:
            # delete old file if it exist
            if self.file_path:
                remove(self.file_path)
                self.file_path = ''

            file_name = data.decode()
            try:
                self.file_path = self.fread_cache.get(file_name, self.tmp_dir, True)
            except FileNotFoundError:
                logger.error(f'file {file_name} not in fread cache')
                self.file_path = ''
        elif subindex == Subindex.DELETE_FILE:
            if self.file_path:
                # delete file from cache and tmp dir
                self.fread_cache.remove(basename(self.file_path))
                remove(self.file_path)
                self.file_path = ''
                logger.info(f'{basename(self.file_path)} was deleted from fread cache')
            else:
                logger.error('fread file path was not set before trying to delete file')
