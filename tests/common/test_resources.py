"""Test the Resource class."""

from oresat_configs import OreSatConfig

from olaf import CanNetwork, Node, Resource


class BadResource(Resource):
    """Bad Resource for testing."""

    def on_start(self) -> None:
        raise RuntimeError("a random exception")

    def on_end(self) -> None:
        raise RuntimeError("a random exception")


class TestResource:
    def test_start_stop(self) -> None:
        """All exception should be caught."""
        od = OreSatConfig().od_db["gps"]
        network = CanNetwork("virtual", "vcan0")
        node = Node(network, od)

        good_res = Resource()
        bad_res = BadResource()

        good_res.start(node)
        bad_res.start(node)

        good_res.end()
        bad_res.end()
