
from ..node import NodeStop
from ...common.resource import Resource


class PowerControlResource(Resource):
    '''Resource for powering off or reseting the system.'''

    def __init__(self):
        super().__init__()

        self.index = 0x3000

    def on_start(self):

        self.node.od['Power control']['Poweroff'].value = False
        self.node.od['Power control']['Reset'].value = 0

        self.node.add_sdo_write_callback(self.index, self.on_write)

    def on_write(self, index: int, subindex: int, value):

        if index != self.index:
            return

        if subindex == 1 and value:
            self.node.stop(NodeStop.POWER_OFF)
        elif subindex == 2:  # reset
            self.node.stop(NodeStop(value))
