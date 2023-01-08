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
        self.node = self.app.node
        self.app.add_resource(FreadResource)
        self.app.start()
        self.fread_sdo = self.node.sdo[self.app.resource.index]

    def tearDown(self):
        self.app.stop()

    def test_read(self):
        self.assertEqual(len(self.app.fread_cache), 0)

        # empty cache
        self.assertIn(self.fread_sdo[Subindex.FILE_NAME.value].phys, ['', 'x'])
        self.assertEqual(self.fread_sdo[Subindex.FILE_DATA.value].phys.decode(), '')
        self.fread_sdo[Subindex.DELETE_FILE.value].phys = True

        # test sdo trasfer of a file that does not exist
        file_name = new_oresat_file('test')
        self.fread_sdo[Subindex.FILE_NAME.value].phys = file_name
        self.fread_sdo[Subindex.FILE_NAME.value].phys = new_oresat_file('abc')
        self.assertEqual(self.fread_sdo[Subindex.FILE_NAME.value].phys, '')
        self.assertEqual(self.fread_sdo[Subindex.FILE_DATA.value].phys.decode(), '')

        # add a file to the cache
        file_name = new_oresat_file('test')
        file_path = '/tmp/' + file_name
        file_data = ''.join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path, 'w') as f:
            f.write(file_data)
        self.app.fread_cache.add(file_path, True)
        self.assertEqual(len(self.app.fread_cache), 1)

        # test sdo trasfer of a file
        self.fread_sdo[Subindex.FILE_NAME.value].phys = basename(file_name)
        self.assertEqual(self.fread_sdo[Subindex.FILE_NAME.value].phys, file_name)
        self.assertEqual(self.fread_sdo[Subindex.FILE_DATA.value].phys.decode(), file_data)
        self.fread_sdo[Subindex.DELETE_FILE.value].phys = True
        self.assertEqual(len(self.app.fread_cache), 0)
