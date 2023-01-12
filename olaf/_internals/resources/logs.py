import tarfile
from os import listdir

from loguru import logger

from ...common.resource import Resource
from ...common.oresat_file import new_oresat_file
from ...common.timer_loop import TimerLoop


class LogsResource(Resource):
    '''Resource for getting logs'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.index = 0x3006
        self.logs_dir_path = '/var/log/journal/'

        self.timer_loop = TimerLoop('logs resource', self._loop, 0.5)
        self.failed = True

    def _loop(self):

        if self.obj.value:
            logger.info('Making a copy of logs')

            tar_file_path = '/tmp/' + new_oresat_file('logs', ext='.tar.xz')

            with tarfile.open(tar_file_path, 'w:xz') as t:
                for i in listdir(self.logs_dir_path):
                    t.add(self.logs_dir_path + '/' + i, arcname=i)

            self.fread_cache.add(tar_file_path, consume=True)
            self.obj.value = False

        return True

    def on_start(self):

        self.obj = self.od[self.index]
        self.obj.value = False  # make sure this is False by default

        self.timer_loop.start()

    def on_end(self):

        self.timer_loop.stop()
