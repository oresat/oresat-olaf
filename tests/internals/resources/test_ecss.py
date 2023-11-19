"""Test ECSS resource."""

import unittest

from olaf._internals.resources.ecss import EcssResource

from . import MockApp


class TestEcssResource(unittest.TestCase):
    """Test ECSS resource."""

    def setUp(self):
        self.app = MockApp()
        self.app.add_resource(EcssResource())
        self.app.start()

    def tearDown(self):
        self.app.stop()

    def test_ecss(self):
        """Test the scet and utc objects callbacks."""

        self.assertNotEqual(self.app.sdo_read("scet", None), 0)
        self.assertNotEqual(self.app.sdo_read("utc", None), 0)
