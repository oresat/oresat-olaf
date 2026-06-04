"""Resource for getting daemons info"""

from __future__ import annotations

from ...common.daemon import DaemonState
from ...common.resource import Resource


class DaemonsResource(Resource):
    """Resource for getting daemons info"""

    def __init__(self) -> None:
        super().__init__()
        self.index = 'daemons'

    def on_start(self) -> None:
        self.node.add_sdo_callbacks(self.index, None, self._on_read, None)

    def _on_read(self, index: int, subindex: int) -> int | None:
        if index != self.index:
            return None

        daemon_manager = self.node.od[self.index]
        total_daemons = daemon_manager['total']
        total_daemons.value = len(self.node.daemons)
        select_daemon = daemon_manager[4]
        # daemon_name = daemon_manager[5]
        # daemon_state = daemon_manager[6]

        if subindex == 2:
            ret = 0
            for i in self.node.daemons.values():
                if i.status == DaemonState.ACTIVE:
                    ret += 1
            return ret
        if subindex == 3:
            ret = 0
            for i in self.node.daemons.values():
                if i.status == DaemonState.ACTIVE:
                    ret += 1
            return ret
        if subindex == 5:
            if select_daemon.value < total_daemons.value:
                return list(self.node.daemons.keys())[select_daemon.value]
        elif subindex == 6:  # noqa: SIM102
            if select_daemon.value < total_daemons.value:
                daemon = list(self.node.daemons.values())[select_daemon.value]
                return daemon.status.value

        return None
