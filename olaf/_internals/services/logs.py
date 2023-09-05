'''Service for getting system logs'''

import os
import tarfile

from loguru import logger

from ...common.service import Service
from ...common.oresat_file import new_oresat_file

TMP_LOGS_FILE = '/tmp/olaf.log'


class LogsService(Service):
    '''Service for getting system logs'''

    def __init__(self):
        super().__init__()

        self.logs_dir_path = '/var/log/journal/'
        self.make_logs_obj = None

    def on_start(self):

        self.make_logs_obj = self.node.od['common_data']['make_logs_file']
        self.make_logs_obj.value = False  # make sure this is False by default

        self.node.add_sdo_callbacks('common_data', 'get_logs', self.on_read_get_logs, None)

    def on_loop(self):

        if self.make_logs_obj.value:
            logger.info('Making a copy of logs')

            tar_file_path = '/tmp/' + new_oresat_file('logs', ext='.tar.xz')

            with tarfile.open(tar_file_path, 'w:xz') as t:
                for i in os.listdir(self.logs_dir_path):
                    t.add(self.logs_dir_path + '/' + i, arcname=i)

            self.node.fread_cache.add(tar_file_path, consume=True)
            self.make_logs_obj.value = False

        self.sleep(0.1)

    def on_read_get_logs(self) -> str:
        '''SDO callback to get a copy of logs since boot.'''

        if not os.path.isfile(TMP_LOGS_FILE):
            return 'no logs'

        with open(TMP_LOGS_FILE, 'r') as f:
            ret = ''.join(reversed(f.readlines()[500:]))

        return ret
