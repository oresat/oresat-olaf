"""Unit tests for the fwrite (aka file write over CAN bus) resource."""

import json
import random
from pathlib import Path

import pytest

from olaf import new_oresat_file
from olaf._internals.resources.fwrite import FwriteResource

from .. import MockApp


class TestFwriteResource:
    @pytest.mark.olaf_resource(res=FwriteResource)
    def test_write(self, app: MockApp, tmp_path: Path) -> None:
        index = "fwrite_cache"
        subindex_len = "length"
        subindex_file_name = "file_name"
        subindex_file_data = "file_data"
        subindex_files_json = "files_json"

        assert len(app.node.fwrite_cache) == 0

        # add a file to the cache
        file_name = new_oresat_file("test")
        file_path = tmp_path / file_name
        file_data = random.randbytes(100)
        file_path.write_bytes(file_data)

        # test sdo trasfer of a file
        app.sdo_write(index, subindex_file_name, file_path.name)
        assert app.sdo_read(index, subindex_file_name) == file_name
        app.sdo_write(index, subindex_file_data, file_data)
        assert len(app.node.fwrite_cache) == 1
        assert app.sdo_read(index, subindex_len) == 1
        file_json = app.sdo_read(index, subindex_files_json)
        assert isinstance(file_json, str)
        file_names = json.loads(file_json)
        assert file_names == [file_name]

        # test sdo trasfer of a file to over write
        app.sdo_write(index, subindex_file_name, file_path.name)
        assert app.sdo_read(index, subindex_file_name) == file_name
        app.sdo_write(index, subindex_file_data, file_data)
        assert len(app.node.fwrite_cache) == 1
        assert app.sdo_read(index, subindex_len) == 1
        file_json = app.sdo_read(index, subindex_files_json)
        assert isinstance(file_json, str)
        file_names = json.loads(file_json)
        assert file_names == [file_name]

        # add another file to the cache
        file_name2 = new_oresat_file("test2")
        file_path2 = tmp_path / file_name2
        file_data2 = random.randbytes(100)
        file_path2.write_bytes(file_data2)

        # test sdo trasfer of a file
        app.sdo_write(index, subindex_file_name, file_path2.name)
        assert app.sdo_read(index, subindex_file_name) == file_name2
        app.sdo_write(index, subindex_file_data, file_data2)
        assert len(app.node.fwrite_cache) == 2
        assert app.sdo_read(index, subindex_len) == 2
        file_json = app.sdo_read(index, subindex_files_json)
        assert isinstance(file_json, str)
        file_names = json.loads(file_json)
        assert file_names == [file_name, file_name2]
