"""Unit tests for the os command (aka bash) service."""

import unittest
from time import sleep

from olaf._internals.services.os_command import OsCommandService, OsCommandState

from . import MockApp


class TestOsCommand(unittest.TestCase):
    """Test the OS command resource."""

    def setUp(self):
        self.app = MockApp()
        self.app.add_service(OsCommandService())
        self.app.start()

        self.index = "os_command"
        self.subindex_command = "command"
        self.subindex_status = "status"
        self.subindex_reply = "reply"

    def tearDown(self):
        self.app.stop()

    def run_os_command(self, command: str):
        """Send os command add give some time to run it"""

        self.app.sdo_write(self.index, self.subindex_command, command)
        for _ in range(50):
            sleep(0.1)
            value = self.app.sdo_read(self.index, self.subindex_status)
            if value != OsCommandState.EXECUTING.value:
                break

    def test_os_command(self):
        """Test the OS command service"""

        self.assertIsNotNone(self.app.sdo_read(self.index, self.subindex_command))
        self.assertIn(
            self.app.sdo_read(self.index, self.subindex_status), [e.value for e in OsCommandState]
        )
        self.assertIsNotNone(self.app.sdo_read(self.index, self.subindex_reply))

        self.run_os_command("ls".encode())
        self.assertEqual(
            self.app.sdo_read(self.index, self.subindex_status), OsCommandState.NO_ERROR_REPLY
        )
        self.assertIsNotNone(self.app.sdo_read(self.index, self.subindex_reply))

        self.run_os_command("invalid-bash-command".encode())
        self.assertEqual(
            self.app.sdo_read(self.index, self.subindex_status), OsCommandState.ERROR_REPLY
        )
        self.assertIsNotNone(self.app.sdo_read(self.index, self.subindex_reply))
