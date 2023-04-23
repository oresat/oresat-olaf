import tarfile
from os import listdir

from loguru import logger

from ...common.resource import Resource
from ...common.oresat_file import new_oresat_file
from ...common.timer_loop import TimerLoop


class LogsResource(Resource):
    '''Resource for getting logs'''

    def __init__(self):
        super().__init__()

        self.index = 0x3006
        self.logs_dir_path = '/var/log/journal/'

        self.timer_loop = TimerLoop('logs resource', self._loop, 500)
        self.failed = True

    def on_start(self):

        self.make_logs_obj = self.node.od[self.index][1]
        self.make_logs_obj.value = False  # make sure this is False by default

        self.node.add_sdo_read_callback(self.index, self.on_read)

        self.timer_loop.start()

    def on_end(self):

        self.timer_loop.stop()

    def _loop(self):

        if self.make_logs_obj.value:
            logger.info('Making a copy of logs')

            tar_file_path = '/tmp/' + new_oresat_file('logs', ext='.tar.xz')

            with tarfile.open(tar_file_path, 'w:xz') as t:
                for i in listdir(self.logs_dir_path):
                    t.add(self.logs_dir_path + '/' + i, arcname=i)

            self.node.fread_cache.add(tar_file_path, consume=True)
            self.make_logs_obj.value = False

        return True

    def on_read(self, index: int, subindex: int):

        if index != self.index and subindex != 2:
            return

        with open('/tmp/olaf.log', 'r') as f:
            ret = ''.join(reversed(f.readlines()[:250]))

        return ret
