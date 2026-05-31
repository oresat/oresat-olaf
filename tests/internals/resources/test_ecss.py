"""Test ECSS resource."""

import pytest

from olaf._internals.resources.ecss import EcssResource

from .. import MockApp


class TestEcssResource:
    @pytest.mark.olaf_resource(res=EcssResource)
    def test_ecss(self, app: MockApp) -> None:
        assert app.sdo_read("scet", None) != 0
        assert app.sdo_read("utc", None) != 0
