from os.path import getsize
from enum import IntEnum, auto

from loguru import logger

from ...common.resource import Resource


class Subindex(IntEnum):
    FREAD_LEN = auto()
    FWRITE_LEN = auto()
    CACHE_SELECTOR = auto()
    FILTER = auto()
    CACHE_LENGTH = auto()
    ITER = auto()
    FILE_NAME = auto()
    FILE_SIZE = auto()
    DELETE_FILE = auto()


class FileCachesResource(Resource):
    '''Resource for interacting with the fread and fwrite caches'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.index = 0x3002
        self.file_caches = [self.fread_cache, self.fwrite_cache]

        # defaults
        self.selector = 0
        self.iter = 0
        self.filter = ''

    def on_read(self, index, subindex, od):

        ret = None

        if index != self.index:
            return ret

        try:
            if subindex == Subindex.FREAD_LEN:
                ret = len(self.fread_cache)
            elif subindex == Subindex.FWRITE_LEN:
                ret = len(self.fwrite_cache)
            elif subindex == Subindex.CACHE_SELECTOR:
                ret = self.selector
            elif subindex == Subindex.FILTER:
                ret = self.filter
            elif subindex == Subindex.CACHE_LENGTH:
                ret = len(self.file_caches[self.selector].files(self.filter))
            elif subindex == Subindex.ITER:
                ret = self.iter
            elif subindex == Subindex.FILE_NAME:
                ret = self.file_caches[self.selector].files(self.filter)[self.iter].name
            elif subindex == Subindex.FILE_SIZE:
                dir_name = self.file_caches[self.selector].dir
                file_name = self.file_caches[self.selector].files(self.filter)[self.iter].name
                file_path = f'{dir_name}/{file_name}'
                ret = getsize(file_path)
        except Exception as exc:
            logger.error(exc)

        return ret

    def on_write(self, index, subindex, od, data):

        if index != self.index:
            return

        try:
            if subindex == Subindex.CACHE_SELECTOR:
                if self.od[index][subindex].decode_raw(data) in [0, 1]:  # check for invalid input
                    self.selector = self.od[index][subindex].decode_raw(data)
            elif subindex == Subindex.FILTER:
                if data == b'\x00':  # just NULL terminator mean no filter
                    self.filter = ''
                    logger.debug('file cache filter clear')
                else:
                    self.filter = data.decode()
                    logger.debug(f'file cache filter now "{self.filter}"')
            elif subindex == Subindex.ITER:
                self.iter = self.od[index][subindex].decode_raw(data)
            elif subindex == Subindex.DELETE_FILE:
                file_name = self.file_caches[self.selector].files(self.filter)[self.iter].name
                self.file_caches[self.selector].remove(file_name)
                logger.info(f'deleted {file_name}')
        except Exception as exc:
            logger.error(exc)
