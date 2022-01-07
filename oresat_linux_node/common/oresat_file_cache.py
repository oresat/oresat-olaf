
import shutil
from os import listdir, remove
from os.path import basename, abspath
from pathlib import Path
from threading import Lock
from copy import deepcopy

from .oresat_file import OreSatFile


class OreSatFileCache:
    '''File cache for OreSat files (by use of :py:class:`OresatFile`). Thread safe.'''

    def __init__(self, dir_path: str):
        '''
        Parameters
        ----------
        dir_path: str
            Directory to use as a OreSat file cache
        '''

        self._dir = abspath(dir_path)
        self._data = []
        self._lock = Lock()

        Path(self._dir).mkdir(parents=True, exist_ok=True)

        for f in listdir(self._dir):
            oresat_file = OreSatFile(self._dir + '/' + f)
            self._data.append(oresat_file)
        self._data = sorted(self._data, reverse=True)

    def __len__(self) -> int:

        length = 0

        with self._lock:
            length = len(self._data)

        return length

    def add(self, file_path: str, consume: bool = False):
        '''Add file to cache

        Parameters
        ----------
        file_path: str
            Path to the file to add to the cache
        consume: bool
            Flag to consume the file when added to the cache
        '''

        new_file_path = self._dir + '/' + basename(file_path)

        with self._lock:
            if consume:
                shutil.move(file_path, new_file_path)
            else:
                shutil.copy(file_path, new_file_path)

            oresat_file = OreSatFile(new_file_path)
            self._data.append(oresat_file)
            self._data = sorted(self._data, reverse=True)

    def remove(self, file_name: str):
        '''Remove file from cache

        Parameters
        ----------
        file_name: str
            Name of the file to remove from the cache
        '''

        with self._lock:
            for f in self._data:
                if f.name == file_name:
                    remove(f.path)
                    self._data.remove(f)

    def peak(self) -> str:
        '''Get the oldest file name'''

        with self._lock:
            if len(self._data) > 0:
                file_name = self._data[0].name
            else:
                file_name = None

        return file_name

    def pop(self, dir_path) -> str:
        '''Pop the oldest file from the cache'''

        with self._lock:
            if len(self._data) > 0:
                file = self._data[0]
                dest = dir_path + '/' + file.name
                shutil.move(file.path, dest)
                self._data.remove(file)
            else:
                dest = None

        return dest

    def get(self, file_name: str, dir_path: str) -> str:
        '''Get the file from the cache and move it a specific directory.

        Parameters
        ----------
        file_name: str
            Name of the file to get from the cache
        dir_path: str
            Name of the directory to move the file to.
        '''

        if dir_path[-1] != '/':
            dir_path += '/'

        dest = None
        with self._lock:
            for f in self._data:
                if f.name == file_name:
                    dest = dir_path + '/' + f.name
                    shutil.move(f.path, dest)
                    self._data.remove(f)
        if not dest:
            raise FileNotFoundError('file', file_name, 'not in cache')

        return dest

    def files(self, keyword='') -> list:
        '''Return a list of files in the cache.

        Parameters
        ----------
        keyword: str
            A keyword to filter by
        path: bool
            Add the absolute path to file list
        '''

        files = []

        with self._lock:
            for f in self._data:
                if keyword and f.keyword != keyword:
                    continue
                files.append(deepcopy(f))

        return files

    def clear(self):
        '''Clear all file in the cache'''

        if len(listdir(self._work_dir)) != 0:
            shutil.rmtree(self._dir, ignore_errors=True)
            Path(self._dir).mkdir(parents=True, exist_ok=True)

    @property
    def dir(self) -> str:
        '''str: Gets the directory path the cache using.'''

        return self._dir
