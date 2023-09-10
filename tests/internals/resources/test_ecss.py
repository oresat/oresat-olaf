import unittest

from olaf._internals.resources.ecss import EcssResource

from . import MockApp


class TestEcssResource(unittest.TestCase):

    def setUp(self):

        self.app = MockApp()
        self.app.add_resource(EcssResource())
        self.app.start()

    def tearDown(self):

        self.app.stop()

    def test_ecss(self):

        self.assertIsNot(self.app.sdo_read('scet', None), 0)
        self.assertIsNot(self.app.sdo_read('utc', None), 0)
