"""Resource for writing oresat files over the CAN bus"""

import json
from os import listdir, remove
from os.path import basename
from pathlib import Path

from loguru import logger

from ...common.oresat_file import OreSatFile
from ...common.resource import Resource


class FwriteResource(Resource):
    """Resource for writing oresat files over the CAN bus"""

    def __init__(self):
        super().__init__()

        self.file_path = ""

        self.tmp_dir = "/tmp/oresat/fwrite"
        Path(self.tmp_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"fwrite tmp dir is {self.tmp_dir}")
        for i in listdir(self.tmp_dir):
            remove(f"{self.tmp_dir}/{i}")

    def on_start(self):
        self.node.add_sdo_callbacks("fwrite_cache", "length", self.on_read_cache_len, None)
        self.node.add_sdo_callbacks("fwrite_cache", "files_json", self.on_read_cache_json, None)
        self.node.add_sdo_callbacks(
            "fwrite_cache", "file_name", self.on_read_file_name, self.on_write_file_name
        )
        self.node.add_sdo_callbacks("fwrite_cache", "file_data", None, self.on_write_file_data)
        self.node.add_sdo_callbacks("fwrite_cache", "remove", None, self.on_write_delete)

    def on_read_cache_len(self) -> int:
        """SDO read callback to get the length of the write cache."""

        return len(self.node.fwrite_cache)

    def on_read_cache_json(self) -> str:
        """SDO read callback to get the list of file in the write cache as a JSON string."""

        return json.dumps([i.name for i in self.node.fwrite_cache.files()])

    def on_read_file_name(self) -> str:
        """SDO read callback to for the selected file to write."""

        return basename(self.file_path)

    def on_write_file_name(self, file_name: str):
        """SDO write callback to select the file to write."""

        try:
            OreSatFile(file_name)  # valiate file name format
            self.file_path = f"{self.tmp_dir}/{file_name}"
        except ValueError:
            logger.error(f"{file_name} is not a valid file name format")
            self.file_path = ""

    def on_write_file_data(self, data: bytes):
        """SDO write callback to write the selected file's data."""

        if not self.file_path:
            logger.error("fwrite file path was not set before file data was sent")
            return

        try:
            with open(self.file_path, "wb") as f:
                f.write(data)
            logger.info(f"receive new file: {basename(self.file_path)}")
            self.node.fwrite_cache.add(self.file_path, consume=True)
        except Exception as e:  # pylint: disable=W0718
            logger.exception(e)

        # clear file data OD obj value to not waste memory
        self.node.od_write("fwrite_cache", "file_data", b"")

    def on_write_delete(self, value: bool):
        """SDO read callback to delete the selected file."""

        if not value:
            return

        if self.file_path:
            # delete file from cache and tmp dir
            self.node.fwrite_cache.remove(basename(self.file_path))
            remove(self.file_path)
            self.file_path = ""
            logger.info(f"{basename(self.file_path)} was deleted from write cache")
        else:
            logger.error("write file path was not set before trying to delete file")
