import json
import random
import string
import unittest
from os.path import basename

from olaf import new_oresat_file
from olaf._internals.resources.fread import FreadResource, Subindex

from . import MockApp


class TestFreadResource(unittest.TestCase):

    def setUp(self):

        self.app = MockApp()
        self.app.add_resource(FreadResource())
        self.app.start()

    def tearDown(self):

        self.app.stop()

    def test_read(self):

        index = self.app.resource.index

        self.assertEqual(len(self.app.node.fread_cache), 0)

        # empty cache
        self.assertIn(self.app.sdo_read(index, Subindex.FILE_NAME.value), ['', 'x'])
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_DATA.value), b'')
        self.assertEqual(self.app.sdo_read(index, Subindex.CRC32.value), 0)
        self.app.sdo_write(index, Subindex.DELETE_FILE.value, True)
        self.assertEqual(self.app.sdo_read(index, Subindex.TOTAL_FILES.value), 0)
        file_names = json.loads(self.app.sdo_read(index, Subindex.FILE_NAMES.value))
        self.assertListEqual(file_names, [])

        # test sdo trasfer of a file that does not exist
        file_name = new_oresat_file('test')
        self.app.sdo_write(index, Subindex.FILE_NAME.value, file_name)
        self.app.sdo_write(index, Subindex.FILE_NAME.value, new_oresat_file('abc'))
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_NAME.value), '')
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_DATA.value), b'')
        self.assertEqual(self.app.sdo_read(index, Subindex.CRC32.value), 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.TOTAL_FILES.value), 0)
        file_names = json.loads(self.app.sdo_read(index, Subindex.FILE_NAMES.value))
        self.assertListEqual(file_names, [])

        # add a file to the cache
        file_name = new_oresat_file('test')
        file_path = '/tmp/' + file_name
        file_data = ''.join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path, 'w') as f:
            f.write(file_data)
        self.app.node.fread_cache.add(file_path, True)
        self.assertEqual(len(self.app.node.fread_cache), 1)

        # test sdo trasfer of a file
        self.app.sdo_write(index, Subindex.FILE_NAME.value, basename(file_name))
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_NAME.value), file_name)
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_DATA.value).decode(), file_data)
        self.assertNotEqual(self.app.sdo_read(index, Subindex.CRC32.value), 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.TOTAL_FILES.value), 1)
        file_names = json.loads(self.app.sdo_read(index, Subindex.FILE_NAMES.value))
        self.assertListEqual(file_names, [file_name])

        # add a another file to the cache
        file_name2 = new_oresat_file('test2')
        file_path2 = '/tmp/' + file_name2
        file_data2 = ''.join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path2, 'w') as f:
            f.write(file_data2)
        self.app.node.fread_cache.add(file_path2, True)
        self.assertEqual(len(self.app.node.fread_cache), 2)

        # test sdo trasfer of both files
        self.app.sdo_write(index, Subindex.FILE_NAME.value, basename(file_name))
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_NAME.value), file_name)
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_DATA.value).decode(), file_data)
        self.assertNotEqual(self.app.sdo_read(index, Subindex.CRC32.value), 0)
        self.app.sdo_write(index, Subindex.FILE_NAME.value, basename(file_name2))
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_NAME.value), file_name2)
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_DATA.value).decode(), file_data2)
        self.assertNotEqual(self.app.sdo_read(index, Subindex.CRC32.value), 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.TOTAL_FILES.value), 2)
        file_names = json.loads(self.app.sdo_read(index, Subindex.FILE_NAMES.value))
        self.assertListEqual(file_names, [file_name, file_name2])

        # delete the first file
        self.app.sdo_write(index, Subindex.FILE_NAME.value, basename(file_name))
        self.app.sdo_write(index, Subindex.DELETE_FILE.value, True)
        self.assertEqual(len(self.app.node.fread_cache), 1)
        self.assertEqual(self.app.sdo_read(index, Subindex.CRC32.value), 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.TOTAL_FILES.value), 1)
        file_names = json.loads(self.app.sdo_read(index, Subindex.FILE_NAMES.value))
        self.assertListEqual(file_names, [file_name2])

        # delete the second file
        self.app.sdo_write(index, Subindex.FILE_NAME.value, basename(file_name2))
        self.app.sdo_write(index, Subindex.DELETE_FILE.value, True)
        self.assertEqual(len(self.app.node.fread_cache), 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.CRC32.value), 0)
        self.assertEqual(self.app.sdo_read(index, Subindex.TOTAL_FILES.value), 0)
        file_names = json.loads(self.app.sdo_read(index, Subindex.FILE_NAMES.value))
        self.assertListEqual(file_names, [])
