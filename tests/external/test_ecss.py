from time import sleep

import canopen

from . import NodeTestCase


class TestECSS(NodeTestCase):
    def test_ecss(self):
        self.assertIsNot(self.sdo[0x2010].raw, 0)
        self.assertIsNot(self.sdo[0x2010].raw, 0)
