"""Test the Resource class."""

import unittest

import can
from oresat_configs import OreSatConfig, OreSatId

from olaf import Node, Resource


class BadResource(Resource):
    """Bad Resource for testing."""

    def on_start(self):
        raise Exception("a random exception")  # pylint: disable=W0719

    def on_end(self):
        raise Exception("a random exception")  # pylint: disable=W0719


class TestResource(unittest.TestCase):
    """Test the Resource class."""

    def test_start_stop(self):
        """All exception should be caught"""

        od = OreSatConfig(OreSatId.ORESAT0).od_db["gps"]
        bus = can.interface.Bus(interface="virtual", channel="vcan0")
        node = Node(od, bus)

        good_res = Resource()
        bad_res = BadResource()

        good_res.start(node)
        bad_res.start(node)

        good_res.end()
        bad_res.end()
