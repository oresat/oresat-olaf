"""File cache class for OreSat files."""

import shutil
from copy import deepcopy
from os import listdir, remove
from os.path import abspath, basename, isfile
from pathlib import Path
from threading import Lock

from .oresat_file import OreSatFile


class OreSatFileCache:
    """File cache for OreSat files (by use of :py:class:`OresatFile`). Thread safe."""

    def __init__(self, dir_path: str):
        """
        Parameters
        ----------
        dir_path: str
            Directory to use as a OreSat file cache. Directory will be made if it does not exist.
        """

        self._dir = abspath(dir_path) + "/"
        self._data = []
        self._lock = Lock()

        if isfile(abspath(self._dir)):
            raise FileExistsError("Cannot create new directory with an existing file name.")

        Path(self._dir).mkdir(parents=True, exist_ok=True)

        for f in listdir(self._dir):
            try:
                oresat_file = OreSatFile(self._dir + f)
                self._data.append(oresat_file)
            except Exception:  # pylint: disable=W0718
                remove(self._dir + f)  # invalid file name
        self._data = sorted(self._data)

    def __len__(self) -> int:
        with self._lock:
            length = len(self._data)

        return length

    def add(self, file_path: str, consume: bool = False):
        """Add file to cache

        Parameters
        ----------
        file_path: str
            Path to the file to add to the cache
        consume: bool
            Flag to consume the file when added to the cache

        Raises
        ------
        FileNotFoundError
            `file_path` was not a valid file path
        """

        new_file_path = self._dir + basename(file_path)

        with self._lock:
            if consume:
                shutil.move(file_path, new_file_path)
            else:
                shutil.copy(file_path, new_file_path)

            oresat_file = OreSatFile(new_file_path)

            overwrite = False
            for i in self._data:
                if i.name == oresat_file.name:
                    overwrite = True

            if not overwrite:
                self._data.append(oresat_file)
                self._data = sorted(self._data)

    def remove(self, file_name: str):
        """Remove a file from cache

        Parameters
        ----------
        file_name: str
            Name of the file to remove from the cache
        """

        with self._lock:
            for f in self._data:
                if f.name == file_name:
                    remove(self._dir + f.name)
                    self._data.remove(f)

    def peek(self) -> str:
        """Get the oldest file name

        Returns
        -------
        str
            Name of the oldest file or an empty string if the cache is empty.
        """

        with self._lock:
            if len(self._data) > 0:
                oldest_file = self._data[0].name
            else:
                oldest_file = ""

        return oldest_file

    def pop(self, dir_path: str, copy: bool = False) -> str:
        """Pop the oldest file from the cache

        Parameters
        ----------
        dir_path: str
            Name of the directory to move the file to.
        copy: bool
            When True the file is copied from the cache, when False the file is moved out of the
            cache.

        Returns
        -------
        str
            File path of the file now in `dir_path` or an empty string if the cache is empty.
        """

        if dir_path[-1] != "/":
            dir_path += "/"

        with self._lock:
            if len(self._data) > 0:
                oldest_file = self._data[0]
                dest = dir_path + oldest_file.name
                if copy:
                    shutil.copy(self._dir + oldest_file.name, dest)
                else:
                    shutil.move(self._dir + oldest_file.name, dest)
                    self._data.remove(oldest_file)
            else:
                dest = ""

        return dest

    def get(self, file_name: str, dir_path: str, copy: bool = False) -> str:
        """Get the file from the cache and move it a specific directory.

        Parameters
        ----------
        file_name: str
            Name of the file to get from the cache
        dir_path: str
            Name of the directory to move the file to.
        copy: bool
            When True the file is copied from the cache, when False the file is moved out of the
            cache.

        Raises
        ------
        FileNotFoundError
            `file_name` was not in cache

        Returns
        -------
        str
            File path of the file now in `dir_path` or an empty string if the cache is empty.
        """

        if dir_path[-1] != "/":
            dir_path += "/"

        dest = None
        with self._lock:
            for f in self._data:
                if f.name == file_name:
                    dest = dir_path + f.name
                    if copy:
                        shutil.copy(self._dir + f.name, dest)
                    else:
                        shutil.move(self._dir + f.name, dest)
                        self._data.remove(f)
        if not dest:
            raise FileNotFoundError(f"file {file_name} not in cache")

        return dest

    def files(self, keyword: str = "") -> list:
        """Return a list of files in the cache.

        Parameters
        ----------
        keyword: str
            A keyword to filter by

        Returns
        -------
        list
            list of :py:class:`OreSatFile` that are in the cache.
        """

        files = []

        with self._lock:
            for f in self._data:
                if keyword and f.keyword != keyword:
                    continue
                files.append(deepcopy(f))

        return files

    def clear(self):
        """Clear all file in the cache"""

        with self._lock:
            shutil.rmtree(self._dir, ignore_errors=True)
            Path(self._dir).mkdir(parents=True, exist_ok=True)
            self._data = []

    @property
    def dir(self) -> str:
        """str: Gets the directory path the cache using."""

        return self._dir[:-1]  # remove the trailing '/'
