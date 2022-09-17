import tarfile
from os import listdir

from loguru import logger

from ..common.resource import Resource
from ..common.oresat_file import new_oresat_file


class LogsResource(Resource):
    '''Resource for getting logs'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.delay = 1.0

        self.index = 0x3006
        self.logs_dir_path = '/var/log/journal/'
        self.obj = self.od[self.index]

    def on_loop(self):

        if self.obj.value:
            self.obj.value = False
            logger.info('Making a copy of logs')

            tar_file_path = '/tmp/' + new_oresat_file('logs', ext='.tar.xz')

            with tarfile.open(tar_file_path, 'w:xz') as t:
                for i in listdir(self.logs_dir_path):
                    t.add(self.logs_dir_path + '/' + i, arcname=i)

            self.fread_cache.add(tar_file_path, consume=True)
