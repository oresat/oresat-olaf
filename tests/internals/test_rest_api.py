"""Test the REST API."""

from collections.abc import Generator

import pytest
from oresat_configs import OreSatConfig
from werkzeug.test import Client

from olaf import CanNetwork, app, rest_api


@pytest.fixture
def client() -> Generator[Client]:
    # Setup OLAF for unit testing.
    config = OreSatConfig()
    od = config.od_db["gps"]
    network = CanNetwork("virtual", "vcan0")

    app.setup(network, od, None, load_core=False)
    rest_api.setup(address="localhost", port=8000)

    app.node._setup_node()

    for i in app._resources:
        i.start(app._node)

    yield rest_api.app.test_client()

    for i in app._resources:
        i.end()

    rest_api._server.server_close()
    app.node._destroy_node()
    app.stop()


class TestRestApi:
    def test_read(self, client: Client) -> None:
        # valid
        res = client.get("/od/0x1000").json  # 0x1000 is manditory
        assert res is not None
        assert "error" not in res
        res = client.get("/od/4096").json  # aka 0x1000
        assert res is not None
        assert "error" not in res
        res = client.get("/od/0x1018/0x1").json  # 0x1018 is manditory
        assert res is not None
        assert "error" not in res

        # invalid
        res = client.get("/od/0x1000/0x1").json  # 0x1000 is manditory
        assert res is not None
        assert "error" in res
        res = client.get("/od/apples").json  # invalid index
        assert res is not None
        assert "error" in res
        res = client.get("/od/0x1010/apples").json  # invalid subindex
        assert res is not None
        assert "error" in res
        res = client.get("/od/0x10").json  # invalid index
        assert res is not None
        assert "error" in res
        res = client.get("/od/0xFFFFFF").json  # invalid index
        assert res is not None
        assert "error" in res

    def test_write(self, client: Client) -> None:
        # valid
        client.put("/od/0x1000", json={"value": 1})
        res = client.get("/od/0x1000").json
        assert res is not None
        assert "error" not in res
        assert res["value"] == 1
        client.put("/od/0x1018/0x1", json={"value": 1})
        res = client.get("/od/0x1018/0x1").json
        assert res is not None
        assert "error" not in res
        assert res["value"] == 1

        # invalid
        res = client.put("/od/apples", json={"value": 0}).json
        assert res is not None
        assert "error" in res
        res = client.put("/od/0x1018/apples", json={"value": 0}).json
        assert res is not None
        assert "error" in res
