"""Service for running OS (bash) commands over CAN bus."""

import subprocess
from enum import Enum

from loguru import logger

from ...common.service import Service


class OsCommandState(Enum):
    """Valid states for OS command as defined by CiA 301 specs."""

    NO_ERROR_NO_REPLY = 0x00
    NO_ERROR_REPLY = 0x01
    ERROR_NO_REPLY = 0x02
    ERROR_REPLY = 0x03
    EXECUTING = 0xFF


class OsCommandService(Service):
    """Service for running OS commands over CAN bus as defined by CiA 301 specs."""

    def __init__(self):
        super().__init__()

        self.command = ""  # internal to prevent overwriting it when running a command
        self.reply_obj_max_len = 10000
        self.failed = False

    def on_start(self):
        self._set_status_and_reply(OsCommandState.ERROR_NO_REPLY.value, b"")
        self.node.add_sdo_callbacks(
            "os_command", "command", self.on_command_read, self.on_command_write
        )

    def on_loop(self):
        if self.node.od_read("os_command", "status") == OsCommandState.EXECUTING.value:
            logger.info("running os command: " + self.command)

            out = subprocess.run(self.command, capture_output=True, shell=True, check=False)
            if out.returncode != 0:  # error
                reply = out.stderr[: self.reply_obj_max_len]
                if reply:
                    status = OsCommandState.ERROR_REPLY.value
                else:
                    status = OsCommandState.ERROR_NO_REPLY.value
            else:  # no error
                reply = out.stdout[: self.reply_obj_max_len]
                if reply:
                    status = OsCommandState.NO_ERROR_REPLY.value
                else:
                    status = OsCommandState.NO_ERROR_NO_REPLY.value

            self._set_status_and_reply(status, reply)

            logger.info(f"os command has completed; ret code: {out.returncode}")

        self.sleep(0.1)

    def on_loop_error(self, error: Exception):
        """On loop error set obj back to default."""

        self.failed = True
        self.command = ""
        self._set_status_and_reply(OsCommandState.ERROR_NO_REPLY.value, b"")
        logger.exception(error)

    def on_command_read(self) -> bytes:
        """SDO read callback for command read."""
        return self.command.encode()

    def on_command_write(self, command: bytes):
        """SDO write callback for command write."""
        logger.error("hi")
        if self.node.od_read("os_command", "status") == OsCommandState.EXECUTING.value:
            logger.error("cannot start another os command when one is running")
            return
        if self.failed:
            logger.error("cannot run os command as service has errored")
            return

        self.command = command.decode()
        self._set_status_and_reply(OsCommandState.EXECUTING.value, b"")

    def _set_status_and_reply(self, status: int, reply: bytes):
        self.node.od_write("os_command", "status", status)
        self.node.od_write("os_command", "reply", reply)
