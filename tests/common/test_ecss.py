import unittest
from time import time

from olaf.common.ecss import scet_int_from_time, scet_int_to_time, \
    utc_int_from_time, utc_int_to_time


class TestECSS(unittest.TestCase):
    def test_scet_time(self):
        now = time()
        scet = scet_int_from_time(now)
        now2 = scet_int_to_time(scet)
        self.assertAlmostEqual(now, now2, 1)

    def test_utc_time(self):
        now = time()
        utc = utc_int_from_time(now)
        now2 = utc_int_to_time(utc)
        self.assertAlmostEqual(now, now2, 1)
