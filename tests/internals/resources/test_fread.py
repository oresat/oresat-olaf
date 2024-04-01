"""Unit tests for the fread (aka file read over CAN bus) resource."""

import json
import random
import string
import unittest
from os.path import basename

from olaf import new_oresat_file
from olaf._internals.resources.fread import FreadResource

from . import MockApp


class TestFreadResource(unittest.TestCase):
    """Test the fread resource."""

    def setUp(self):
        self.app = MockApp()
        self.app.add_resource(FreadResource())
        self.app.start()

    def tearDown(self):
        self.app.stop()

    def test_read(self):
        """Test file reads."""

        index = "fread_cache"
        subindex_len = "length"
        subindex_remove = "remove"
        subindex_file_name = "file_name"
        subindex_file_data = "file_data"
        subindex_files_json = "files_json"

        self.assertEqual(len(self.app.node.fread_cache), 0)

        # empty cache
        self.assertEqual(self.app.sdo_read(index, subindex_file_name), "")
        self.assertEqual(self.app.sdo_read(index, subindex_file_data), b"")
        self.app.sdo_write(index, subindex_remove, True)
        self.assertEqual(self.app.sdo_read(index, subindex_len), 0)
        file_names = json.loads(self.app.sdo_read(index, subindex_files_json))
        self.assertListEqual(file_names, [])

        # test sdo trasfer of a file that does not exist
        file_name = new_oresat_file("test")
        self.app.sdo_write(index, subindex_file_name, file_name)
        self.app.sdo_write(index, subindex_file_name, new_oresat_file("abc"))
        self.assertEqual(self.app.sdo_read(index, subindex_file_name), "")
        self.assertEqual(self.app.sdo_read(index, subindex_file_data), b"")
        self.assertEqual(self.app.sdo_read(index, subindex_len), 0)
        file_names = json.loads(self.app.sdo_read(index, subindex_files_json))
        self.assertListEqual(file_names, [])

        # add a file to the cache
        file_name = new_oresat_file("test")
        file_path = "/tmp/" + file_name
        file_data = "".join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path, "w") as f:
            f.write(file_data)
        self.app.node.fread_cache.add(file_path, True)
        self.assertEqual(len(self.app.node.fread_cache), 1)

        # test sdo trasfer of a file
        self.app.sdo_write(index, subindex_file_name, basename(file_name))
        self.assertEqual(self.app.sdo_read(index, subindex_file_name), file_name)
        self.assertEqual(self.app.sdo_read(index, subindex_file_data).decode(), file_data)
        self.assertEqual(self.app.sdo_read(index, subindex_len), 1)
        file_names = json.loads(self.app.sdo_read(index, subindex_files_json))
        self.assertListEqual(file_names, [file_name])

        # add a another file to the cache
        file_name2 = new_oresat_file("test2")
        file_path2 = "/tmp/" + file_name2
        file_data2 = "".join(random.choice(string.ascii_letters) for i in range(100))
        with open(file_path2, "w") as f:
            f.write(file_data2)
        self.app.node.fread_cache.add(file_path2, True)
        self.assertEqual(len(self.app.node.fread_cache), 2)

        # test sdo trasfer of both files
        self.app.sdo_write(index, subindex_file_name, basename(file_name))
        self.assertEqual(self.app.sdo_read(index, subindex_file_name), file_name)
        self.assertEqual(self.app.sdo_read(index, subindex_file_data).decode(), file_data)
        self.app.sdo_write(index, subindex_file_name, basename(file_name2))
        self.assertEqual(self.app.sdo_read(index, subindex_file_name), file_name2)
        self.assertEqual(self.app.sdo_read(index, subindex_file_data).decode(), file_data2)
        self.assertEqual(self.app.sdo_read(index, subindex_len), 2)
        file_names = json.loads(self.app.sdo_read(index, subindex_files_json))
        self.assertListEqual(file_names, [file_name, file_name2])

        # delete the first file
        self.app.sdo_write(index, subindex_file_name, basename(file_name))
        self.app.sdo_write(index, subindex_remove, True)
        self.assertEqual(len(self.app.node.fread_cache), 1)
        self.assertEqual(self.app.sdo_read(index, subindex_len), 1)
        file_names = json.loads(self.app.sdo_read(index, subindex_files_json))
        self.assertListEqual(file_names, [file_name2])

        # delete the second file
        self.app.sdo_write(index, subindex_file_name, basename(file_name2))
        self.app.sdo_write(index, subindex_remove, True)
        self.assertEqual(len(self.app.node.fread_cache), 0)
        self.assertEqual(self.app.sdo_read(index, subindex_len), 0)
        file_names = json.loads(self.app.sdo_read(index, subindex_files_json))
        self.assertListEqual(file_names, [])
