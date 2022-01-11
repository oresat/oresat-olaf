import tarfile
from os import geteuid, listdir
from time import time, clock_settime, CLOCK_REALTIME

import canopen
from loguru import logger

from ..common.resource import Resource
from ..common.oresat_file import new_oresat_file
from ..common.oresat_file_cache import OreSatFileCache


class LogsResource(Resource):
    '''Resource for getting logs'''

    def __init__(self, node: canopen.LocalNode, fread_cache: OreSatFileCache):

        super().__init__(node, 'Logs', 1.0)

        self.index = 0x3006
        self.logs_dir_path = '/var/log/journal/'
        self.obj = node.object_dictionary[self.index]
        self.fread_cache = fread_cache

    def on_loop(self):

        if self.obj.value:
            self.obj.value = False
            logger.info('Making a copy of logs')

            tar_file_path = '/tmp/' + new_oresat_file('logs', ext='.tar.xz')

            with tarfile.open(tar_file_path, 'w:xz') as t:
                for i in listdir(self.logs_dir_path):
                    t.add(self.logs_dir_path + '/' + i, arcname=i)

            self.fread_cache.add(tar_file_path, consume=True)
