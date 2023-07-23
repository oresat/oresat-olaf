import tarfile
from os import listdir

from loguru import logger

from ...common.service import Service
from ...common.oresat_file import new_oresat_file


class LogsService(Service):
    '''Service for getting logs'''

    def __init__(self):
        super().__init__()

        self.index = 0x3006
        self.logs_dir_path = '/var/log/journal/'

    def on_start(self):

        self.make_logs_obj = self.node.od[self.index][1]
        self.make_logs_obj.value = False  # make sure this is False by default

        self.node.add_sdo_read_callback(self.index, self.on_read)

    def on_loop(self):

        if self.make_logs_obj.value:
            logger.info('Making a copy of logs')

            tar_file_path = '/tmp/' + new_oresat_file('logs', ext='.tar.xz')

            with tarfile.open(tar_file_path, 'w:xz') as t:
                for i in listdir(self.logs_dir_path):
                    t.add(self.logs_dir_path + '/' + i, arcname=i)

            self.node.fread_cache.add(tar_file_path, consume=True)
            self.make_logs_obj.value = False

        self.sleep(0.5)

    def on_read(self, index: int, subindex: int):

        if index != self.index and subindex != 2:
            return

        with open('/tmp/olaf.log', 'r') as f:
            ret = ''.join(reversed(f.readlines()[:250]))

        return ret
