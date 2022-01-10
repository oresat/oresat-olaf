import unittest
from time import sleep

from oresat_linux_node.apps.ecss import ECSSApp

from . import TestNode


class TestECSSApp(unittest.TestCase):
    def setUp(self):
        self.oresat = TestNode()
        self.node = self.oresat.node
        self.oresat.add_app(ECSSApp(self.node))
        self.oresat.start()

    def tearDown(self):
        self.oresat.stop()

    def test_ecss(self):

        self.assertIsNot(self.node.sdo[0x2010].raw, 0)
        self.assertIsNot(self.node.sdo[0x2010].raw, 0)
