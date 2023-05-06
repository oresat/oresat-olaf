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

    def __init__(self):
        super().__init__()

        self.selector = 0
        self.iter = 0
        self.filter = ''
        self.index = 0x3002

    def on_start(self):

        self.file_caches = [self.node.fread_cache, self.node.fwrite_cache]
        self.node.add_sdo_read_callback(self.index, self.on_read)
        self.node.add_sdo_write_callback(self.index, self.on_write)

    def on_read(self, index: int, subindex: int):

        ret = None

        if index != self.index:
            return ret

        try:
            if subindex == Subindex.FREAD_LEN:
                ret = len(self.node.fread_cache)
            elif subindex == Subindex.FWRITE_LEN:
                ret = len(self.node.fwrite_cache)
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
        except Exception as e:
            logger.error(e)

        return ret

    def on_write(self, index: int, subindex: int, value):

        if index != self.index:
            return

        try:
            if subindex == Subindex.CACHE_SELECTOR:
                if value in [0, 1]:  # check for invalid input
                    self.selector = value
            elif subindex == Subindex.FILTER:
                if value == '':  # aka no filter
                    self.filter = ''
                    logger.debug('file cache filter clear')
                else:
                    self.filter = value
                    logger.debug(f'file cache filter now "{self.filter}"')
            elif subindex == Subindex.ITER:
                self.iter = value
            elif subindex == Subindex.DELETE_FILE:
                file_name = self.file_caches[self.selector].files(self.filter)[self.iter].name
                self.file_caches[self.selector].remove(file_name)
                logger.info(f'deleted {file_name}')
        except Exception as e:
            logger.exception(e)
