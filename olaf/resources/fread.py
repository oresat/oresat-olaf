from os import remove, listdir
from os.path import basename
from pathlib import Path

import canopen
from loguru import logger

from ..common.resource import Resource
from ..common.oresat_file_cache import OreSatFileCache


class FreadResource(Resource):
    '''Resource for readings file over the CAN bus'''

    def __init__(self,
                 node: canopen.LocalNode,
                 fread_cache: OreSatFileCache,
                 tmp_dir: str = '/tmp/oresat/fread'):

        super().__init__(node, 'Fread', -1.0)

        if tmp_dir == '/':
            raise ValueError('tmp_dir cannot be root dir')

        if tmp_dir[-1] != '/':
            tmp_dir += '/'

        self.fread_cache = fread_cache

        self.tmp_dir = tmp_dir
        Path(self.tmp_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f'fread tmp_dir is {self.tmp_dir}')
        for i in listdir(self.tmp_dir):
            remove(self.tmp_dir + i)

        self.index = 0x3003
        self.sub_file_name = 0x1
        self.sub_file_data = 0x2
        self.sub_delete_file = 0x3

        self.file_path = ''

    def on_read(self, index, subindex, od):

        ret = None

        if index != self.index:
            return ret

        if not self.file_path:
            logger.error('fread file path was not set before trying to read info')
            return ret

        if subindex == self.sub_file_name:
            ret = basename(self.file_path)
        elif subindex == self.sub_file_data:
            try:
                with open(self.file_path, 'rb') as f:
                    ret = f.read()
            except FileNotFoundError as exc:
                logger.error(exc)

        return ret

    def on_write(self, index, subindex, od, data):

        if index != self.index:
            return

        if subindex == self.sub_file_name:
            # delete old file if it exist
            if self.file_path:
                remove(self.file_path)
                self.file_path = ''

            file_name = data.decode()
            try:
                self.file_path = self.fread_cache.get(file_name, self.tmp_dir, True)
            except FileNotFoundError:
                logger.error(f'file {file_name} not in fread cache')
        elif subindex == self.sub_delete_file:
            if self.file_path:
                # delete file from cache and tmp dir
                self.fread_cache.remove(basename(self.file_path))
                remove(self.file_path)
                self.file_path = ''
            else:
                logger.error('fread file path was not set before trying to delete file')
