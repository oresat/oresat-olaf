"""Resource for getting daemons info"""

from ...common.daemon import DaemonState
from ...common.resource import Resource


class DaemonsResource(Resource):
    """Resource for getting daemons info"""

    def __init__(self):
        super().__init__()

        self.index = 0x3005
        self._total_daemons_obj = None
        self._select_daemon_obj = None
        self._daemon_name_obj = None
        self._daemon_state_obj = None

    def on_start(self):
        daemon_manager_obj = self.node.od[self.index]
        self._total_daemons_obj = daemon_manager_obj[1]
        self._select_daemon_obj = daemon_manager_obj[4]
        self._daemon_name_obj = daemon_manager_obj[5]
        self._daemon_state_obj = daemon_manager_obj[6]

        self._total_daemons_obj.value = len(self.node.daemons)

        self.node.add_sdo_read_callback(self.index, self._on_read)

    def _on_read(self, index: int, subindex: int):
        ret = None

        if index != self.index:
            return ret

        if subindex == 2:
            ret = 0
            for i in self.node.daemons.values():
                if i.status == DaemonState.ACTIVE:
                    ret += 1
        elif subindex == 3:
            ret = 0
            for i in self.node.daemons.values():
                if i.status == DaemonState.ACTIVE:
                    ret += 1
        elif subindex == 5:
            if self._select_daemon_obj.value < self._total_daemons_obj.value:
                ret = list(self.node.daemons.keys())[self._select_daemon_obj.value]
        elif subindex == 6:
            if self._select_daemon_obj.value < self._total_daemons_obj.value:
                daemon = list(self.node.daemons.values())[self._select_daemon_obj.value]
                ret = daemon.status.value

        return ret
