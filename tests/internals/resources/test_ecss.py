import unittest

from olaf._internals.resources.ecss import ECSSResource

from . import MockApp


class TestECSSResource(unittest.TestCase):

    def setUp(self):

        self.app = MockApp()
        self.app.add_resource(ECSSResource())
        self.app.start()

    def tearDown(self):

        self.app.stop()

    def test_ecss(self):

        self.assertIsNot(self.app.sdo_read(0x2010, None), 0)
        self.assertIsNot(self.app.sdo_read(0x2011, None), 0)
