"""Test the ECSS functions."""

from time import time

import pytest

from olaf.canopen.ecss import (
    scet_int_from_time,
    scet_int_to_time,
    utc_int_from_time,
    utc_int_to_time,
)


class TestEcss:
    def test_scet_time(self) -> None:
        now = time()
        scet = scet_int_from_time(now)
        now2 = scet_int_to_time(scet)
        assert now2 == pytest.approx(now)

    def test_utc_time(self) -> None:
        now = time()
        utc = utc_int_from_time(now)
        now2 = utc_int_to_time(utc)
        assert now2 == pytest.approx(now)
