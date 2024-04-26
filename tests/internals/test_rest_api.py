"""Test the REST API."""

import unittest

from oresat_configs import OreSatConfig, OreSatId

from olaf import CanNetwork, app, rest_api


class TestRestApi(unittest.TestCase):
    """Test the REST API."""

    @classmethod
    def setUpClass(cls):
        # Setup OLAF for unit testing.
        config = OreSatConfig(OreSatId.ORESAT0_5)
        od = config.od_db["gps"]
        network = CanNetwork("virtual", "vcan0")
        app.setup(network, od, None, False)
        rest_api.setup(address="localhost", port=8000)

        cls.client = rest_api.app.test_client()

        app.node._setup_node()

        for i in app._resources:
            i.start(app._node)

    @classmethod
    def tearDownClass(cls):
        for i in app._resources:
            i.end()

        app.node._destroy_node()
        app.stop()

    def test_read(self):
        """Test reading a value from an object."""

        # valid
        self.assertNotIn("error", self.client.get("/od/0x1000").json)  # 0x1000 is manditory
        self.assertNotIn("error", self.client.get("/od/4096").json)  # aka 0x1000
        self.assertNotIn("error", self.client.get("/od/0x1018/0x1").json)  # 0x1018 is manditory

        # invalid
        self.assertIn("error", self.client.get("/od/0x1000/0x1").json)  # 0x1000 is manditory
        self.assertIn("error", self.client.get("/od/apples").json)  # invalid index
        self.assertIn("error", self.client.get("/od/0x1010/apples").json)  # invalid subindex
        self.assertIn("error", self.client.get("/od/0x10").json)  # invalid index
        self.assertIn("error", self.client.get("/od/0xFFFFFF").json)  # invalid index

    def test_write(self):
        """Test writing a value to an object."""

        # valid
        self.client.put("/od/0x1000", json={"value": 1})
        res = self.client.get("/od/0x1000")
        self.assertNotIn("error", res.json)
        self.assertEqual(res.json["value"], 1)
        self.client.put("/od/0x1018/0x1", json={"value": 1})
        res = self.client.get("/od/0x1018/0x1")
        self.assertNotIn("error", res.json)
        self.assertEqual(res.json["value"], 1)

        # invalid
        res = self.client.put("/od/apples", json={"value": 0})
        self.assertIn("error", res.json)
        res = self.client.put("/od/0x1018/apples", json={"value": 0})
        self.assertIn("error", res.json)
