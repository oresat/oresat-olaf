from os import remove, listdir
from os.path import basename
from pathlib import Path

import canopen
from loguru import logger

from ..common.resource import Resource
from ..common.oresat_file_cache import OreSatFileCache


class FwriteResource(Resource):
    '''Resource for writing files over the CAN bus'''

    def __init__(self,
                 node: canopen.LocalNode,
                 fwrite_cache: OreSatFileCache,
                 tmp_dir: str = '/tmp/oresat/fwrite'):

        super().__init__(node, 'Fwrite', -1.0)

        if tmp_dir == '/':
            raise ValueError('tmp_dir cannot be root dir')

        if tmp_dir[-1] != '/':
            tmp_dir += '/'

        self.fwrite_cache = fwrite_cache
        self.tmp_dir = tmp_dir
        Path(self.tmp_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f'fwrite tmp_dir is {self.tmp_dir}')
        for i in listdir(self.tmp_dir):
            remove(self.tmp_dir + i)

        self.index = 0x3004
        self.sub_file_name = 0x1
        self.sub_file_data = 0x2

        self.file_path = ''

    def on_read(self, index, subindex, od):

        ret = None

        if index == self.index and self.file_path and subindex == self.sub_file_name:
            ret = basename(self._file_path)

        return ret

    def on_write(self, index, subindex, od, data):

        if index != self.index:
            return

        if subindex == self.sub_file_name:
            file_name = data.decode()
            self.file_path = self.tmp_dir + '/' + file_name
        elif subindex == self.sub_file_data:
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
            self.node.object_dictionary[index][subindex].value = ''
            self.node.sdo[index][subindex].value = ''
