"""Unit tests for the os command (aka bash) service."""

from time import sleep

import pytest

from olaf._internals.services.os_command import OsCommandService, OsCommandState

from .. import MockApp


class TestOsCommand:
    index = "os_command"
    subindex_command = "command"
    subindex_status = "status"
    subindex_reply = "reply"

    @pytest.mark.olaf_resource(res=OsCommandService)
    def run_os_command(self, app: MockApp, command: bytes) -> None:
        app.sdo_write(self.index, self.subindex_command, command)
        for _ in range(50):
            sleep(0.1)
            value = app.sdo_read(self.index, self.subindex_status)
            if value != OsCommandState.EXECUTING.value:
                break

    @pytest.mark.olaf_resource(res=OsCommandService)
    def test_os_command(self, app: MockApp) -> None:
        assert app.sdo_read(self.index, self.subindex_command) is not None
        assert app.sdo_read(self.index, self.subindex_status) in [e.value for e in OsCommandState]
        assert app.sdo_read(self.index, self.subindex_reply) is not None

        self.run_os_command(app, b"ls")
        status = app.sdo_read(self.index, self.subindex_status)
        assert OsCommandState(status) == OsCommandState.NO_ERROR_REPLY
        reply = app.sdo_read(self.index, self.subindex_reply)
        assert reply is not None

        self.run_os_command(app, b"invalid-bash-command")
        status = app.sdo_read(self.index, self.subindex_status)
        assert OsCommandState(status) == OsCommandState.ERROR_REPLY
        reply = app.sdo_read(self.index, self.subindex_reply)
        assert reply is not None
