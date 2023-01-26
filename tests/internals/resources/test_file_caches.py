import random
import string
import unittest

from olaf import new_oresat_file
from olaf._internals.resources.file_caches import FileCachesResource, Subindex

from . import MockApp


class TestFileCachesResource(unittest.TestCase):
    def setUp(self):
        self.app = MockApp()
        self.node = self.app.node
        self.app.add_resource(FileCachesResource)
        self.app.start()
        self.file_caches_sdo = self.node.sdo[self.app.resource.index]

    def tearDown(self):
        self.app.stop()

    def test_empty_caches(self):
        self.assertEqual(len(self.app.fread_cache), 0)
        self.assertEqual(len(self.app.fwrite_cache), 0)

        # check cache len
        self.assertEqual(self.file_caches_sdo[Subindex.FREAD_LEN.value].phys, 0)
        self.assertEqual(self.file_caches_sdo[Subindex.FWRITE_LEN.value].phys, 0)
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 0)
        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 0
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys, 0)
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 0)

        # check cache selector
        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 1
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys, 1)
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 0)

        # invalid
        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 2
        # self.assertIn(self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys, [0, 1])

        # check filter
        self.file_caches_sdo[Subindex.FILTER.value].phys = ''
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 0)
        self.file_caches_sdo[Subindex.FILTER.value].phys = 'abc'
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 0)
        self.file_caches_sdo[Subindex.FILTER.value].phys = ''
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 0)

        # check iterator
        self.assertEqual(self.file_caches_sdo[Subindex.ITER.value].phys, 0)
        self.assertNotEqual(self.file_caches_sdo[Subindex.ITER.value].phys, 1)
        self.assertNotEqual(self.file_caches_sdo[Subindex.ITER.value].phys, 100)

        # check file name
        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 0
        # self.assertEqual(self.file_caches_sdo[Subindex.FILE_NAME.value].phys, '')
        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 1
        # self.assertEqual(self.file_caches_sdo[Subindex.FILE_NAME.value].phys, '')

        # check file size
        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 0
        self.assertEqual(self.file_caches_sdo[Subindex.FILE_SIZE.value].phys, 0)
        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 1
        self.assertEqual(self.file_caches_sdo[Subindex.FILE_SIZE.value].phys, 0)

        self.file_caches_sdo[Subindex.DELETE_FILE.value].phys = True

    def test_non_empty_caches(self):

        # add files to a cache
        self.assertEqual(self.file_caches_sdo[Subindex.FREAD_LEN.value].phys, 0)
        file_name = new_oresat_file('test')
        file_path = '/tmp/' + file_name
        file_data = ''.join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path, 'w') as f:
            f.write(file_data)
        self.app.fread_cache.add(file_path, True)
        self.assertEqual(self.file_caches_sdo[Subindex.FREAD_LEN.value].phys, 1)
        file_name2 = new_oresat_file('test2')
        file_path = '/tmp/' + file_name2
        file_data = ''.join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path, 'w') as f:
            f.write(file_data)
        self.app.fread_cache.add(file_path, True)
        self.assertEqual(self.file_caches_sdo[Subindex.FREAD_LEN.value].phys, 2)

        # check cache len
        self.assertEqual(self.file_caches_sdo[Subindex.FREAD_LEN.value].phys, 2)
        self.assertEqual(self.file_caches_sdo[Subindex.FWRITE_LEN.value].phys, 0)
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 2)

        # check cache selector
        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 0
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys, 0)
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 2)
        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 1
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys, 1)
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 0)

        # check filter
        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 0
        self.file_caches_sdo[Subindex.FILTER.value].phys = ''
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 2)
        self.file_caches_sdo[Subindex.FILTER.value].phys = 'test'
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 1)
        self.file_caches_sdo[Subindex.FILTER.value].phys = 'abc'
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 0)
        self.file_caches_sdo[Subindex.FILTER.value].phys = ''
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 2)

        # check iterator
        self.assertEqual(self.file_caches_sdo[Subindex.ITER.value].phys, 0)
        self.assertNotEqual(self.file_caches_sdo[Subindex.ITER.value].phys, 1)
        self.assertEqual(self.file_caches_sdo[Subindex.ITER.value].phys, 0)

        # check file names
        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 0
        self.assertIn(self.file_caches_sdo[Subindex.FILE_NAME.value].phys, [file_name, file_name2])
        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 1
        # self.assertEqual(self.file_caches_sdo[Subindex.FILE_NAME.value].phys, '')

        # check file sizes
        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 0
        self.assertNotEqual(self.file_caches_sdo[Subindex.FILE_SIZE.value].phys, 0)
        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 1
        self.assertEqual(self.file_caches_sdo[Subindex.FILE_SIZE.value].phys, 0)

        self.file_caches_sdo[Subindex.CACHE_SELECTOR.value].phys = 0

        # delete 1st file
        self.file_caches_sdo[Subindex.DELETE_FILE.value].phys = True
        self.assertEqual(self.file_caches_sdo[Subindex.FREAD_LEN.value].phys, 1)
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 1)

        # delete 2nd file
        self.file_caches_sdo[Subindex.DELETE_FILE.value].phys = True
        self.assertEqual(self.file_caches_sdo[Subindex.FREAD_LEN.value].phys, 0)
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 0)

        # delete on empty
        self.file_caches_sdo[Subindex.DELETE_FILE.value].phys = True
        self.assertEqual(self.file_caches_sdo[Subindex.FREAD_LEN.value].phys, 0)
        self.assertEqual(self.file_caches_sdo[Subindex.CACHE_LENGTH.value].phys, 0)
