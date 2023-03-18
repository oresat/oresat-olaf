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
        self.app.sdo_write(index, Subindex.DELETE_FILE.value, True)

        # test sdo trasfer of a file that does not exist
        file_name = new_oresat_file('test')
        self.app.sdo_write(index, Subindex.FILE_NAME.value, file_name)
        self.app.sdo_write(index, Subindex.FILE_NAME.value, new_oresat_file('abc'))
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_NAME.value), '')
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_DATA.value), b'')

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
        self.app.sdo_write(index, Subindex.DELETE_FILE.value, True)
        self.assertEqual(len(self.app.node.fread_cache), 0)
