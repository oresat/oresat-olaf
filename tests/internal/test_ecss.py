from time import time

import pytest

from oresat_linux_node.common.ecss import scet_int_from_time, scet_int_to_time, \
    utc_int_from_time, utc_int_to_time


def test_scet_time():

    now = time()

    scet = scet_int_from_time(now)
    now2 = scet_int_to_time(scet)

    assert now == pytest.approx(now2, 0.0001)


def test_utc_time():

    now = time()

    scet = utc_int_from_time(now)
    now2 = utc_int_to_time(scet)

    assert now == pytest.approx(now2, 0.0001)
