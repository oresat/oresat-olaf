from collections.abc import Generator
from pathlib import Path

import pytest

from . import MockApp


@pytest.fixture
def app(request: pytest.FixtureRequest, tmp_path: Path) -> Generator[MockApp]:
    marker = request.node.get_closest_marker("olaf_resource")
    if marker is None:
        raise RuntimeError("Missing test olaf_resource marker")
    else:
        resource = marker.kwargs['res']

    app = MockApp(tmp_path, resource())
    app.start()
    yield app
    app.stop()
