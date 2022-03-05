import os
import unittest

from olaf.common.oresat_file import new_oresat_file, OreSatFile


class TestOreSatFile(unittest.TestCase):
    def test_new_oresat_file(self):

        file = new_oresat_file('keyword', 'test', 100)
        self.assertEqual(file, 'test_keyword_100')

        file = new_oresat_file('keyword', 'test', 100, 'txt')
        self.assertEqual(file, 'test_keyword_100.txt')

        file = new_oresat_file('keyword', 'test', 100, '.txt')
        self.assertEqual(file, 'test_keyword_100.txt')

        self.assertIsNotNone(new_oresat_file('test'))

    def test_oresat_file(self):

        name = 'name_test_12345.txt'
        file = OreSatFile(name)
        self.assertEqual(file.board, 'name')
        self.assertEqual(file.keyword, 'test')
        self.assertEqual(file.date, 12345.0)
        self.assertEqual(file.extension, '.txt')
        self.assertEqual(file.name, name)

        name = 'name_test_12345.tar.xz'
        file = OreSatFile(name)
        self.assertEqual(file.date, 12345.0)
        self.assertEqual(file.extension, '.tar.xz')

        name = '/this/is/test/name_test_123'
        file = OreSatFile(name)
        self.assertEqual(file.board, 'name')
        self.assertEqual(file.keyword, 'test')
        self.assertEqual(file.date, 123.0)
        self.assertEqual(file.extension, '')
        self.assertEqual(file.name, os.path.basename(name))

        with self.assertRaises(ValueError):
            OreSatFile('nametest12345')

        with self.assertRaises(ValueError):
            OreSatFile('__')

        with self.assertRaises(ValueError):
            OreSatFile('__12345')

        with self.assertRaises(ValueError):
            OreSatFile('_test_12345')

        with self.assertRaises(ValueError):
            OreSatFile('name__12345')

        with self.assertRaises(ValueError):
            OreSatFile('name_test_')

        self.assertLess(OreSatFile('name_test_12345.txt'), OreSatFile('name_test_23456.txt'))
        self.assertGreater(OreSatFile('name_test_23456.txt'), OreSatFile('name_test_12345.txt'))
