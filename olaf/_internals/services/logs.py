"""Service for the getting system logs over CAN."""

import logging
import os
import tarfile

from ...common.oresat_file import new_oresat_file
from ...common.service import Service

logger = logging.getLogger(__file__)

TMP_LOGS_FILE = "/tmp/olaf.log"


def get_log_file_handler() -> logging.FileHandler:
    """Get the boot log file handler and clean up temp log file used by LogsService."""
    if os.path.isfile(TMP_LOGS_FILE):
        os.remove(TMP_LOGS_FILE)
    return logging.FileHandler(TMP_LOGS_FILE)


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
