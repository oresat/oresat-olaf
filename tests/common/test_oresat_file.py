"""Test the OreSat file class."""

import os
import unittest

from olaf.common.oresat_file import OreSatFile, new_oresat_file


class TestOreSatFile(unittest.TestCase):
    """Test the OreSat file class."""

    def test_new_oresat_file(self):
        """Test the new_oresat_file functions."""

        file = new_oresat_file("keyword", "test", 100)
        self.assertEqual(file, "test_keyword_100000")

        file = new_oresat_file("keyword", "test", 100, "txt")
        self.assertEqual(file, "test_keyword_100000.txt")

        file = new_oresat_file("keyword", "test", 100, ".txt")
        self.assertEqual(file, "test_keyword_100000.txt")

        self.assertIsNotNone(new_oresat_file("test"))

    def test_oresat_file(self):
        """Test the OreSatFile class constructor."""

        name = "name_test_12345.txt"
        file = OreSatFile(name)
        self.assertEqual(file.card, "name")
        self.assertEqual(file.keyword, "test")
        self.assertEqual(file.date, 12.345)
        self.assertEqual(file.extension, ".txt")
        self.assertEqual(file.name, name)

        name = "name_test_12345.tar.xz"
        file = OreSatFile(name)
        self.assertEqual(file.date, 12.345)
        self.assertEqual(file.extension, ".tar.xz")

        name = "/this/is/test/name_test_123"
        file = OreSatFile(name)
        self.assertEqual(file.card, "name")
        self.assertEqual(file.keyword, "test")
        self.assertEqual(file.date, 0.123)
        self.assertEqual(file.extension, "")
        self.assertEqual(file.name, os.path.basename(name))

        with self.assertRaises(ValueError):
            OreSatFile("nametest12345")

        with self.assertRaises(ValueError):
            OreSatFile("__")

        with self.assertRaises(ValueError):
            OreSatFile("__12345")

        with self.assertRaises(ValueError):
            OreSatFile("_test_12345")

        with self.assertRaises(ValueError):
            OreSatFile("name__12345")

        with self.assertRaises(ValueError):
            OreSatFile("name_test_")

        self.assertLess(OreSatFile("name_test_12345.txt"), OreSatFile("name_test_23456.txt"))
        self.assertGreater(OreSatFile("name_test_23456.txt"), OreSatFile("name_test_12345.txt"))
