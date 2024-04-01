"""Unit tests for the fwrite (aka file write over CAN bus) resource."""

import json
import random
import string
import unittest
from os import remove
from os.path import basename

from olaf import new_oresat_file
from olaf._internals.resources.fwrite import FwriteResource

from . import MockApp


class TestFwriteResource(unittest.TestCase):
    """Test the fwrite resource."""

    def setUp(self):
        self.app = MockApp()
        self.app.add_resource(FwriteResource())
        self.app.start()

    def tearDown(self):
        self.app.stop()

    def test_write(self):
        """Test file writes."""

        index = "fwrite_cache"
        subindex_len = "length"
        subindex_file_name = "file_name"
        subindex_file_data = "file_data"
        subindex_files_json = "files_json"

        self.assertEqual(len(self.app.node.fwrite_cache), 0)

        # add a file to the cache
        file_name = new_oresat_file("test")
        file_path = "/tmp/" + file_name
        file_data = "".join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path, "w") as f:
            f.write(file_data)

        # test sdo trasfer of a file
        self.app.sdo_write(index, subindex_file_name, basename(file_name))
        self.assertEqual(self.app.sdo_read(index, subindex_file_name), file_name)
        self.app.sdo_write(index, subindex_file_data, file_data.encode())
        self.assertEqual(len(self.app.node.fwrite_cache), 1)
        self.assertEqual(self.app.sdo_read(index, subindex_len), 1)
        file_names = json.loads(self.app.sdo_read(index, subindex_files_json))
        self.assertListEqual(file_names, [file_name])

        # test sdo trasfer of a file to over write
        self.app.sdo_write(index, subindex_file_name, basename(file_name))
        self.assertEqual(self.app.sdo_read(index, subindex_file_name), file_name)
        self.app.sdo_write(index, subindex_file_data, file_data.encode())
        self.assertEqual(len(self.app.node.fwrite_cache), 1)
        self.assertEqual(self.app.sdo_read(index, subindex_len), 1)
        file_names = json.loads(self.app.sdo_read(index, subindex_files_json))
        self.assertListEqual(file_names, [file_name])

        # remove test file
        remove(file_path)

        # add another file to the cache
        file_name2 = new_oresat_file("test2")
        file_path2 = "/tmp/" + file_name2
        file_data2 = "".join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path2, "w") as f:
            f.write(file_data2)

        # test sdo trasfer of a file
        self.app.sdo_write(index, subindex_file_name, basename(file_name2))
        self.assertEqual(self.app.sdo_read(index, subindex_file_name), file_name2)
        self.app.sdo_write(index, subindex_file_data, file_data2.encode())
        self.assertEqual(len(self.app.node.fwrite_cache), 2)
        self.assertEqual(self.app.sdo_read(index, subindex_len), 2)
        file_names = json.loads(self.app.sdo_read(index, subindex_files_json))
        self.assertListEqual(file_names, [file_name, file_name2])

        # remove test file
        remove(file_path2)
