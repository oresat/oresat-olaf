"""Unit tests for the fread (aka file read over CAN bus) resource."""

import json
import random
from pathlib import Path

import pytest

from olaf import new_oresat_file
from olaf._internals.resources.fread import FreadResource

from .. import MockApp


class TestFreadResource:
    @pytest.mark.olaf_resource(res=FreadResource)
    def test_read(self, app: MockApp, tmp_path: Path) -> None:
        index = "fread_cache"
        subindex_len = "length"
        subindex_remove = "remove"
        subindex_file_name = "file_name"
        subindex_file_data = "file_data"
        subindex_files_json = "files_json"

        assert len(app.node.fread_cache) == 0

        # empty cache
        assert app.sdo_read(index, subindex_file_name) == ""
        assert app.sdo_read(index, subindex_file_data) == b""
        app.sdo_write(index, subindex_remove, value=True)
        assert app.sdo_read(index, subindex_len) == 0
        file_json = app.sdo_read(index, subindex_files_json)
        assert isinstance(file_json, str)
        file_names = json.loads(file_json)
        assert file_names == []

        # test sdo trasfer of a file that does not exist
        file_name = new_oresat_file("test")
        app.sdo_write(index, subindex_file_name, file_name)
        app.sdo_write(index, subindex_file_name, new_oresat_file("abc"))
        assert app.sdo_read(index, subindex_file_name) == ""
        assert app.sdo_read(index, subindex_file_data) == b""
        assert app.sdo_read(index, subindex_len) == 0
        file_json = app.sdo_read(index, subindex_files_json)
        assert isinstance(file_json, str)
        file_names = json.loads(file_json)
        assert file_names == []

        # add a file to the cache
        file_name = new_oresat_file("test")
        file_path = tmp_path / file_name
        file_data = random.randbytes(100)
        file_path.write_bytes(file_data)
        app.node.fread_cache.add(file_path, consume=True)
        assert len(app.node.fread_cache) == 1

        # test sdo trasfer of a file
        app.sdo_write(index, subindex_file_name, file_path.name)
        assert app.sdo_read(index, subindex_file_name) == file_name
        assert app.sdo_read(index, subindex_file_data) == file_data
        assert app.sdo_read(index, subindex_len) == 1
        file_json = app.sdo_read(index, subindex_files_json)
        assert isinstance(file_json, str)
        file_names = json.loads(file_json)
        assert file_names == [file_name]

        # add a another file to the cache
        file_name2 = new_oresat_file("test2")
        file_path2 = tmp_path / file_name2
        file_data2 = random.randbytes(100)
        file_path2.write_bytes(file_data2)
        app.node.fread_cache.add(file_path2, consume=True)
        assert len(app.node.fread_cache) == 2

        # test sdo trasfer of both files
        app.sdo_write(index, subindex_file_name, file_path.name)
        assert app.sdo_read(index, subindex_file_name) == file_name
        assert app.sdo_read(index, subindex_file_data) == file_data
        app.sdo_write(index, subindex_file_name, file_path2.name)
        assert app.sdo_read(index, subindex_file_name) == file_name2
        assert app.sdo_read(index, subindex_file_data) == file_data2
        assert app.sdo_read(index, subindex_len) == 2
        file_json = app.sdo_read(index, subindex_files_json)
        assert isinstance(file_json, str)
        file_names = json.loads(file_json)
        assert file_names == [file_name, file_name2]

        # delete the first file
        app.sdo_write(index, subindex_file_name, file_path.name)
        app.sdo_write(index, subindex_remove, value=True)
        assert len(app.node.fread_cache) == 1
        assert app.sdo_read(index, subindex_len) == 1
        file_json = app.sdo_read(index, subindex_files_json)
        assert isinstance(file_json, str)
        file_names = json.loads(file_json)
        assert file_names == [file_name2]

        # delete the second file
        app.sdo_write(index, subindex_file_name, file_path2.name)
        app.sdo_write(index, subindex_remove, value=True)
        assert len(app.node.fread_cache) == 0
        assert app.sdo_read(index, subindex_len) == 0
        file_json = app.sdo_read(index, subindex_files_json)
        assert isinstance(file_json, str)
        file_names = json.loads(file_json)
        assert file_names == []
