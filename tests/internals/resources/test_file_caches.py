import random
import string
import unittest

from olaf import new_oresat_file
from olaf._internals.resources.file_caches import FileCachesResource, Subindex

from . import MockApp


class TestFileCachesResource(unittest.TestCase):

    def setUp(self):

        self.app = MockApp()
        self.app.add_resource(FileCachesResource())
        self.app.start()

    def tearDown(self):

        self.app.stop()

    def test_empty_caches(self):

        self.assertEqual(len(self.app.node.fread_cache), 0)
        self.assertEqual(len(self.app.node.fwrite_cache), 0)

        index = self.app.resource.index

        # check cache len
        self.assertEqual(self.app.sdo_read(index, Subindex.FREAD_LEN.value), 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.FWRITE_LEN.value), 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 0)
        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_SELECTOR.value), 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 0)

        # check cache selector
        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 1)
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_SELECTOR.value), 1)
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 0)

        # invalid
        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 2)
        # self.assertIn(self.app.sdo_read(index, Subindex.CACHE_SELECTOR.value), [0, 1])

        # check filter
        self.app.sdo_write(index, Subindex.FILTER.value, '')
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 0)
        self.app.sdo_write(index, Subindex.FILTER.value, 'abc')
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 0)
        self.app.sdo_write(index, Subindex.FILTER.value, '')
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 0)

        # check iterator
        self.assertEqual(self.app.sdo_read(index, Subindex.ITER.value), 0)
        self.assertNotEqual(self.app.sdo_read(index, Subindex.ITER.value), 1)
        self.assertNotEqual(self.app.sdo_read(index, Subindex.ITER.value), 100)

        # check file name
        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 0)
        # self.assertEqual(self.app.sdo_read(index, Subindex.FILE_NAME.value), '')
        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 1)
        # self.assertEqual(self.app.sdo_read(index, Subindex.FILE_NAME.value), '')

        # check file size
        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_SIZE.value), 0)
        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 1)
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_SIZE.value), 0)

        self.app.sdo_write(index, Subindex.DELETE_FILE.value, True)

    def test_non_empty_caches(self):

        index = self.app.resource.index

        # add files to a cache
        self.assertEqual(self.app.sdo_read(index, Subindex.FREAD_LEN.value), 0)
        file_name = new_oresat_file('test')
        file_path = '/tmp/' + file_name
        file_data = ''.join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path, 'w') as f:
            f.write(file_data)
        self.app.node.fread_cache.add(file_path, True)
        self.assertEqual(self.app.sdo_read(index, Subindex.FREAD_LEN.value), 1)
        file_name2 = new_oresat_file('test2')
        file_path = '/tmp/' + file_name2
        file_data = ''.join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path, 'w') as f:
            f.write(file_data)
        self.app.node.fread_cache.add(file_path, True)
        self.assertEqual(self.app.sdo_read(index, Subindex.FREAD_LEN.value), 2)

        # check cache len
        self.assertEqual(self.app.sdo_read(index, Subindex.FREAD_LEN.value), 2)
        self.assertEqual(self.app.sdo_read(index, Subindex.FWRITE_LEN.value), 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 2)

        # check cache selector
        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_SELECTOR.value), 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 2)
        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 1)
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_SELECTOR.value), 1)
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 0)

        # check filter
        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 0)
        self.app.sdo_write(index, Subindex.FILTER.value, '')
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 2)
        self.app.sdo_write(index, Subindex.FILTER.value, 'test')
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 1)
        self.app.sdo_write(index, Subindex.FILTER.value, 'abc')
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 0)
        self.app.sdo_write(index, Subindex.FILTER.value, '')
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 2)

        # check iterator
        self.assertEqual(self.app.sdo_read(index, Subindex.ITER.value), 0)
        self.assertNotEqual(self.app.sdo_read(index, Subindex.ITER.value), 1)
        self.assertEqual(self.app.sdo_read(index, Subindex.ITER.value), 0)

        # check file names
        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 0)
        self.assertIn(self.app.sdo_read(index, Subindex.FILE_NAME.value), [file_name, file_name2])
        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 1)
        # self.assertEqual(self.app.sdo_read(index, Subindex.FILE_NAME.value), '')

        # check file sizes
        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 0)
        self.assertNotEqual(self.app.sdo_read(index, Subindex.FILE_SIZE.value), 0)
        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 1)
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_SIZE.value), 0)

        self.app.sdo_write(index, Subindex.CACHE_SELECTOR.value, 0)

        # delete 1st file
        self.app.sdo_write(index, Subindex.DELETE_FILE.value, True)
        self.assertEqual(self.app.sdo_read(index, Subindex.FREAD_LEN.value), 1)
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 1)

        # delete 2nd file
        self.app.sdo_write(index, Subindex.DELETE_FILE.value, True)
        self.assertEqual(self.app.sdo_read(index, Subindex.FREAD_LEN.value), 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 0)

        # delete on empty
        self.app.sdo_write(index, Subindex.DELETE_FILE.value, True)
        self.assertEqual(self.app.sdo_read(index, Subindex.FREAD_LEN.value), 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.CACHE_LENGTH.value), 0)
