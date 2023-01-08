import random
import string
import unittest
from os import remove
from os.path import basename

from olaf import new_oresat_file
from olaf._internals.resources.fwrite import FwriteResource, Subindex

from . import MockApp


class TestFwriteResource(unittest.TestCase):
    def setUp(self):
        self.app = MockApp()
        self.node = self.app.node
        self.app.add_resource(FwriteResource)
        self.app.start()
        self.fwrite_sdo = self.node.sdo[self.app.resource.index]

    def tearDown(self):
        self.app.stop()

    def test_write(self):
        self.assertEqual(len(self.app.fwrite_cache), 0)

        # add a file to the cache
        file_name = new_oresat_file('test')
        file_path = '/tmp/' + file_name
        file_data = ''.join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path, 'w') as f:
            f.write(file_data)

        # test sdo trasfer of a file
        self.fwrite_sdo[Subindex.FILE_NAME.value].phys = basename(file_name)
        self.assertEqual(self.fwrite_sdo[Subindex.FILE_NAME.value].phys, file_name)
        self.fwrite_sdo[Subindex.FILE_DATA.value].phys = file_data.encode()
        self.assertEqual(len(self.app.fwrite_cache), 1)

        # test sdo trasfer of a file to over write
        self.fwrite_sdo[Subindex.FILE_NAME.value].phys = basename(file_name)
        self.assertEqual(self.fwrite_sdo[Subindex.FILE_NAME.value].phys, file_name)
        self.fwrite_sdo[Subindex.FILE_DATA.value].phys = file_data.encode()
        self.assertEqual(len(self.app.fwrite_cache), 1)

        # remove test file
        remove(file_path)

        # add another file to the cache
        file_name = new_oresat_file('test2')
        file_path = '/tmp/' + file_name
        file_data = ''.join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path, 'w') as f:
            f.write(file_data)

        # test sdo trasfer of a file
        self.fwrite_sdo[Subindex.FILE_NAME.value].phys = basename(file_name)
        self.assertEqual(self.fwrite_sdo[Subindex.FILE_NAME.value].phys, file_name)
        self.fwrite_sdo[Subindex.FILE_DATA.value].phys = file_data.encode()
        self.assertEqual(len(self.app.fwrite_cache), 2)

        # remove test file
        remove(file_path)
