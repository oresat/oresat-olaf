import unittest

from olaf._internals.resources.ecss import ECSSResource

from . import MockApp


class TestECSSResource(unittest.TestCase):
    def setUp(self):
        self.app = MockApp()
        self.node = self.app.node
        self.app.add_resource(ECSSResource)
        self.app.start()

    def tearDown(self):
        self.app.stop()

    def test_ecss(self):

        self.assertIsNot(self.node.sdo[0x2010].raw, 0)
        self.assertIsNot(self.node.sdo[0x2011].raw, 0)
