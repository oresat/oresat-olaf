"""Test the Resource class."""

import unittest

from oresat_configs import OreSatConfig, OreSatId

from olaf import CanNetwork, Node, Resource


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
        network = CanNetwork("virtual", "vcan0")
        node = Node(network, od)

        good_res = Resource()
        bad_res = BadResource()

        good_res.start(node)
        bad_res.start(node)

        good_res.end()
        bad_res.end()
