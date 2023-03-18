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
        self.app.add_resource(FwriteResource())
        self.app.start()

    def tearDown(self):

        self.app.stop()

    def test_write(self):

        index = self.app.resource.index

        self.assertEqual(len(self.app.node.fwrite_cache), 0)

        # add a file to the cache
        file_name = new_oresat_file('test')
        file_path = '/tmp/' + file_name
        file_data = ''.join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path, 'w') as f:
            f.write(file_data)

        # test sdo trasfer of a file
        self.app.sdo_write(index, Subindex.FILE_NAME.value, basename(file_name))
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_NAME.value), file_name)
        self.app.sdo_write(index, Subindex.FILE_DATA.value, file_data.encode())
        self.assertEqual(len(self.app.node.fwrite_cache), 1)

        # test sdo trasfer of a file to over write
        self.app.sdo_write(index, Subindex.FILE_NAME.value, basename(file_name))
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_NAME.value), file_name)
        self.app.sdo_write(index, Subindex.FILE_DATA.value, file_data.encode())
        self.assertEqual(len(self.app.node.fwrite_cache), 1)

        # remove test file
        remove(file_path)

        # add another file to the cache
        file_name = new_oresat_file('test2')
        file_path = '/tmp/' + file_name
        file_data = ''.join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path, 'w') as f:
            f.write(file_data)

        # test sdo trasfer of a file
        self.app.sdo_write(index, Subindex.FILE_NAME.value, basename(file_name))
        self.assertEqual(self.app.sdo_read(index, Subindex.FILE_NAME.value), file_name)
        self.app.sdo_write(index, Subindex.FILE_DATA.value, file_data.encode())
        self.assertEqual(len(self.app.node.fwrite_cache), 2)

        # remove test file
        remove(file_path)
