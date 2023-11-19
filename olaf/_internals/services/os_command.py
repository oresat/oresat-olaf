"""Service for running OS (bash) commands over CAN bus."""

import subprocess
from enum import IntEnum

from loguru import logger

from ...common.service import Service


class OsCommandState(IntEnum):
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
        self.state_obj = None
        self.reply_obj = None

    def on_start(self):
        self.state_obj = self.node.od["os_command"]["status"]
        self.state_obj.value = OsCommandState.NO_ERROR_NO_REPLY.value
        self.reply_obj = self.node.od["os_command"]["reply"]
        self.reply_obj.value = b""
        self.node.add_sdo_callbacks(
            "os_command", "command", self.on_command_read, self.on_command_write
        )

    def on_loop(self):
        if self.state_obj.value == OsCommandState.EXECUTING:
            logger.info("running os command: " + self.command)

            out = subprocess.run(self.command, capture_output=True, shell=True, check=False)
            if out.returncode != 0:  # error
                self.reply_obj.value = out.stderr[: self.reply_obj_max_len]
                if self.reply_obj.value:
                    self.state_obj.value = OsCommandState.ERROR_REPLY.value
                else:
                    self.state_obj.value = OsCommandState.ERROR_NO_REPLY.value
            else:  # no error
                self.reply_obj.value = out.stdout[: self.reply_obj_max_len]
                if self.reply_obj.value:
                    self.state_obj.value = OsCommandState.NO_ERROR_REPLY.value
                else:
                    self.state_obj.value = OsCommandState.NO_ERROR_NO_REPLY.value

            logger.info(f"os command has completed; ret code: {out.returncode}")

        self.sleep(0.1)

    def on_loop_error(self, error: Exception):
        """On loop error set obj back to default."""

        self.failed = True
        self.command = b""
        self.state_obj.value = OsCommandState.ERROR_NO_REPLY
        self.reply_obj.value = b""
        logger.exception(error)

    def on_command_read(self) -> bytes:
        """SDO read callback for command read."""
        return self.command.encode()

    def on_command_write(self, command: bytes):
        """SDO write callback for command write."""
        if self.state_obj.value == OsCommandState.EXECUTING:
            logger.error("cannot start another os command when one is running")
            return
        if self.failed:
            logger.error("cannot run os command as service has errored")
            return

        self.command = command.decode()
        self.state_obj.value = OsCommandState.EXECUTING.value
        self.reply_obj.value = b""
