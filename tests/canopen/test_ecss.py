"""Test the ECSS functions."""

import unittest
from time import time

from olaf.canopen.ecss import (
    scet_int_from_time,
    scet_int_to_time,
    utc_int_from_time,
    utc_int_to_time,
)


class TestEcss(unittest.TestCase):
    """Test the ECSS functions."""

    def test_scet_time(self):
        """Test the ECSS SCET time functions."""

        now = time()
        scet = scet_int_from_time(now)
        now2 = scet_int_to_time(scet)
        self.assertAlmostEqual(now, now2, 1)

    def test_utc_time(self):
        """Test the ECSS UTC time functions."""

        now = time()
        utc = utc_int_from_time(now)
        now2 = utc_int_to_time(utc)
        self.assertAlmostEqual(now, now2, 1)
