"""Resource for readings oresat files over the CAN bus"""

import json
from os import listdir, remove
from os.path import basename
from pathlib import Path

from loguru import logger

from ...common.resource import Resource


class FreadResource(Resource):
    """Resource for readings oresat files over the CAN bus"""

    def __init__(self):
        super().__init__()

        self.file_path = ""
        self.tmp_dir = "/tmp/oresat/fread"
        Path(self.tmp_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"fread tmp dir is {self.tmp_dir}")
        for i in listdir(self.tmp_dir):
            remove(f"{self.tmp_dir}/{i}")

    def on_start(self):
        self.node.add_sdo_callbacks("fread_cache", "length", self.on_read_cache_len, None)
        self.node.add_sdo_callbacks("fread_cache", "files_json", self.on_read_cache_json, None)
        self.node.add_sdo_callbacks(
            "fread_cache", "file_name", self.on_read_file_name, self.on_write_file_name
        )
        self.node.add_sdo_callbacks("fread_cache", "file_data", self.on_read_file_data, None)
        self.node.add_sdo_callbacks("fread_cache", "remove", None, self.on_write_delete)

    def on_read_cache_len(self) -> int:
        """SDO read callback to get the length of the fread cache."""

        return len(self.node.fread_cache)

    def on_read_cache_json(self) -> str:
        """SDO read callback to get the list of file in the fread cache as a JSON string."""

        return json.dumps([i.name for i in self.node.fread_cache.files()])

    def on_read_file_name(self) -> str:
        """SDO read callback to for the selected file to read."""

        return basename(self.file_path)

    def on_write_file_name(self, file_name: str):
        """SDO write callback to select the file to read."""

        try:
            self.file_path = self.node.fread_cache.get(file_name, self.tmp_dir, True)
        except FileNotFoundError:
            logger.error(f"file {file_name} not in fread cache")
            self.file_path = ""

    def on_read_file_data(self) -> bytes:
        """SDO read callback to get the selected file's data."""

        if not self.file_path:
            logger.debug("fread file path was not set before trying to read file data")
            return b""

        ret = b""
        try:
            with open(self.file_path, "rb") as f:
                ret = f.read()
        except FileNotFoundError:
            logger.error(f"file {self.file_path} does not exist")
        return ret

    def on_write_delete(self, value: bool):
        """SDO read callback to delete the selected file."""

        if not value:
            return

        if self.file_path:
            # delete file from cache and tmp dir
            self.node.fread_cache.remove(basename(self.file_path))
            remove(self.file_path)
            self.file_path = ""
            logger.info(f"{basename(self.file_path)} was deleted from fread cache")
        else:
            logger.error("fread file path was not set before trying to delete file")
