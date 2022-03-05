import unittest
from time import sleep

from olaf.resources.ecss import ECSSResource

from . import TestApp


class TestECSSResource(unittest.TestCase):
    def setUp(self):
        self.app = TestApp()
        self.node = self.app.node
        self.app.add_resource(ECSSResource(self.node))
        self.app.start()

    def tearDown(self):
        self.app.stop()

    def test_ecss(self):

        self.assertIsNot(self.node.sdo[0x2010].raw, 0)
        self.assertIsNot(self.node.sdo[0x2010].raw, 0)
