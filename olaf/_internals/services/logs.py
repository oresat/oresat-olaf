"""Service for getting system logs"""

import os
import tarfile

from loguru import logger

from ...common.oresat_file import new_oresat_file
from ...common.service import Service

TMP_LOGS_FILE = "/tmp/olaf.log"


def logger_tmp_file_setup(level: str):
    """Congfigure logger to save to tmp file for LogsService"""

    # log file for log service (overrides each time app starts)
    if os.path.isfile(TMP_LOGS_FILE):
        os.remove(TMP_LOGS_FILE)
    logger.add(TMP_LOGS_FILE, level=level, backtrace=True)


class LogsService(Service):
    """Service for getting system logs"""

    def __init__(self):
        super().__init__()

        self.logs_dir_path = "/var/log/journal/"
        self.make_file_obj = None

    def on_start(self):
        self.make_file_obj = self.node.od["logs"]["make_file"]
        self.make_file_obj.value = False  # make sure this is False by default

        self.node.add_sdo_callbacks("logs", "since_boot", self.on_read_since_boot, None)

    def on_loop(self):
        if self.make_file_obj.value:
            logger.info("Making a copy of logs")

            tar_file_path = "/tmp/" + new_oresat_file("logs", ext=".tar.xz")

            with tarfile.open(tar_file_path, "w:xz") as t:
                for i in os.listdir(self.logs_dir_path):
                    t.add(self.logs_dir_path + "/" + i, arcname=i)

            self.node.fread_cache.add(tar_file_path, consume=True)
            self.make_file_obj.value = False

        self.sleep(0.1)

    def on_read_since_boot(self) -> str:
        """SDO callback to get a copy of logs since boot."""

        if not os.path.isfile(TMP_LOGS_FILE):
            return "no logs"

        with open(TMP_LOGS_FILE, "r") as f:
            ret = "".join(reversed(f.readlines()[-500:]))

        return ret
