'''Linux updater daemon'''

import json
import logging
import tarfile
import subprocess
from os import listdir, remove
from os.path import abspath, basename, isfile
from shutil import rmtree
from pathlib import Path
from enum import IntEnum

from .common.oresat_file import OreSatFile, new_oresat_file
from .common.oresat_file_cache import OreSatFileCache

INSTRUCTIONS_FILE = 'instructions.txt'
'''The instructions file that is always in a OreSat Linux update archive. It
defines the order instructions are ran in and how it is ran.'''

INSTRUCTIONS = {
    'BASH_SCRIPT': 'bash',
    'DPKG_INSTALL': 'dpkg -i',
    'DPKG_REMOVE': 'dpkg -r',
    'DPKG_PURGE': 'dpkg -P',
}
'''All the valid instruction. Values are the commands.'''

INSTRUCTIONS_WITH_FILES = [
    'BASH_SCRIPT',
    'DPKG_INSTALL',
]
'''The list of instructions from INSTRUCTIONS that require file(s).'''

OLU_STATUS_KEYWORD = 'olu-status'
DPKG_STATUS_KEYWORD = 'dpkg-status'
DPKG_STATUS_FILE = '/var/lib/dpkg/status'


class UpdaterError(Exception):
    '''An error occurred in Updater class.'''


class UpdaterState(IntEnum):
    '''The integer value Updater's update() will return'''

    UPDATE_SUCCESSFUL = 0x0
    '''The last update was successfully installed. Default State.'''
    PRE_UPDATE_FAILED = 0x1
    '''The last update failed during the inital non critical section. Either the was an error using the
    file cache, when opening tarfile, or reading the instructions file.'''
    UPDATED_FAILED = 0x2
    '''The update failed during the critical section. The updater fail while following the
    instructions.'''
    UPDATING = 0xFF
    '''Updater is updating'''


class Updater:
    '''The OreSat Linux updater. Allows OreSat Linux boards to be update thru update archives.

    While this could be replaced with a couple of functions. Having a object with properties, allow
    for easy to get status info while updating.
    '''

    def __init__(self, work_dir: str, cache_dir: str):
        '''
        Parameters
        ----------
        work_dir: str
            Directory to use a the working dir. Should be a abslute path.
        cache_dir: str
            Directory to store update archives in. Should be a abslute path.
        '''

        # make update_archives for cache dir
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        self._cache_dir = abspath(cache_dir)
        logging.debug('updater cache dir ' + self._cache_dir)

        # make update_archives for work dir
        Path(work_dir).mkdir(parents=True, exist_ok=True)
        self._work_dir = abspath(work_dir)
        logging.debug('updater work dir ' + self._work_dir)

        self._cache = OreSatFileCache(cache_dir)

        self._state = UpdaterState.UPDATE_SUCCESSFUL
        self._update_archive = ''
        self._total_instructions = 0
        self._instruction_index = 0
        self._instruction_percent = 0
        self._command = ''

    def _clear_work_dir(self):
        '''Clear the working directory.'''

        logging.info('clearing working directory')
        rmtree(self._work_dir, ignore_errors=True)
        Path(self._work_dir).mkdir(parents=True, exist_ok=True)

    def add_update_archive(self, file_path: str) -> bool:
        '''Copies update archive into the update archive cache.

        Parameters
        ----------
        file_path: str
            The absolute path to update archive for the updater to copy.

        Returns
        -------
        bool
            True if a file was added or False on failure.
        '''

        ret = True
        file_path = abspath(file_path)  # make sure it is a absolute path
        file_name = basename(file_path)

        try:
            self._cache.add(file_path)
        except FileNotFoundError:
            logging.error(file_name + ' is a invalid file')
            ret = False

        return ret

    def update(self):
        '''Run a update.

        If there are file aleady in the working directory, it will try to find
        and resume the update, otherwise it will get the oldest archive from
        the update archive cache and run it.

        If the update fails, the cache will be cleared, as it is asume all
        newer updates require the failed updated to be run successfully first.

        Raises
        ------
        UpdaterError
            A error occurred when updating.
        '''

        if self._state == UpdaterState.UPDATING:
            raise UpdaterError('can\'t start an new update while already updating')

        update_archive_file_path = ''
        self._state = UpdaterState.UPDATING
        self._update_archive = ''
        self._total_instructions = 0
        self._instruction_index = 0
        self._instruction_percent = 0
        self._command = ''

        # something in working dir, see if it an update to resume
        file_list = listdir(self._work_dir)
        if len(file_list) != 0:
            logging.info('files found in working dir')

            # find update archive in work directory
            for file_name in file_list:
                if is_update_archive(file_name):
                    self._update_archive = file_name
                    update_archive_file_path = self._work_dir + '/' + file_name
                    logging.info('resuming update with ' + file_name)
                    break

            if update_archive_file_path == '':  # Nothing to resume
                logging.info('nothing to resume')
                self._clear_work_dir()

        # if not resuming, get new update archive from cache
        if update_archive_file_path == '' and len(self._cache) != 0:
            update_archive_file_path = self._cache.get(self._work_dir)
            self._update_archive = basename(update_archive_file_path)
            logging.info('got ' + self._update_archive + ' from cache')

        if update_archive_file_path == '':  # nothing to do
            logging.info('no update to resume or in cache')
            self._state = UpdaterState.UPDATE_SUCCESSFUL
            return

        logging.info('extracting files from update')
        try:
            self._extract_update_archive(update_archive_file_path)
        except UpdaterError as exc:
            logging.error(exc)
            self._clear_work_dir()
            self._state = UpdaterState.PRE_UPDATE_FAILED
            return

        logging.info('reading instructions file')
        try:
            commands = self._read_instructions()
        except UpdaterError as exc:
            logging.error(exc)
            self._clear_work_dir()
            self._state = UpdaterState.PRE_UPDATE_FAILED
            return

        logging.info('running instructions')
        try:
            # No turn back point, the update is starting!!!
            # If anything fails/errors the board's software could break.
            # All errors are log at critical level.
            self._run_instructions(commands)
        except UpdaterError as exc:
            logging.critical(exc)
            self._clear_work_dir()
            self._cache.clear()
            self._state = UpdaterState.UPDATE_FAILED
            return

        logging.info('update ' + self._update_archive + ' was successful')
        self._clear_work_dir()
        self._update_archive = ''

        self._state = UpdaterState.UPDATE_SUCCESSFUL

    def _extract_update_archive(self, file_path: str) -> str:
        '''Open the update archive file.

        Parameters
        ----------
        file_path: str
            Path to the update archive.

        Raises
        ------
        UpdaterError
            Invalid update archive.

        Returns
        -------
        str
            The contents of the instructions file.
        '''

        file_name = basename(file_path)

        if not is_update_archive(file_path):
            raise UpdaterError(file_name + ' does not follow OreSat file name standards')

        try:
            with tarfile.open(file_path, 'r:xz') as t:
                t.extractall(self._work_dir)
        except tarfile.TarError:
            raise UpdaterError(file_name + ' is a invalid .xztar.xz')

        instructions_file_path = self._work_dir + INSTRUCTIONS_FILE
        if not isfile(instructions_file_path):
            raise UpdaterError(file_name + ' is missing an instructions file')

        return instructions_file_path

    def _read_instructions(self) -> list:
        '''Read the instructions file, validates the instructions, and makes the commands.

        Parameters
        ----------
        instruction: str
            path to the instructions file

        Raises
        ------
        UpdaterError
            An instruction has failed

        Returns
        -------
        str
            List of bash commands to run
        '''

        commands = []

        try:
            instructions = json.loads(self._work_dir + '/' + INSTRUCTIONS_FILE)
        except json.JSONDecodeError:
            raise UpdaterError('instructions file was mising or did not contain a valid json')

        # valid instructions and make commands
        for i in instructions:
            if i not in instructions:
                raise UpdaterError(i + ' is not a valid instruction type')
            if not isinstance(instructions[i], list):
                raise UpdaterError(i + ' values is not a list')

            work_dir_path = ' ' + self._work_dir + '/'

            if i in INSTRUCTIONS_WITH_FILES:
                # make sure all file exist
                for j in instructions[i]:
                    if isfile(self._work_dir + '/' + j):
                        UpdaterError(i + ' is missing ' + j)

                command = INSTRUCTIONS[i] + ' ' + work_dir_path.join(instructions[i])
            else:
                command = INSTRUCTIONS[i] + ' ' + ' '.join(instructions[i])

            commands.append(command)

        return commands

    def _run_instructions(self, commands: list):
        '''Run the instructions made by `_read_instructions.

        Parameters
        ----------
        commands: list
            List of bash commands to run

        Raises
        ------
        UpdaterError
            An instruction has failed
        `'''

        self._total_instructions = len(commands)
        self._instruction_percent = 0

        for command in commands:
            logging.info(command)

            self._command = command
            self._instruction_index = commands.index(command)

            out = subprocess.run(command, capture_output=True, shell=True)

            if out.returncode != 0:
                for line in out.stderr.decode('utf-8').split('\n'):
                    if len(line) != 0:
                        logging.error(line)

                raise UpdaterError('update failed!')

            for line in out.stdout.decode('utf-8').split('\n'):
                if len(line) != 0:
                    logging.info(line)

            self.instruction_percent = self.total_instructions // self._instruction_index

        self._instruction_percent = 100

    def make_status_archive(self) -> str:
        '''Make status tar file with a copy of the dpkg status file and a file with the list of
        updates in cache.

        Returns
        -------
        str
            Path to new status file or empty string on failure.
        '''

        dpkg_status = False
        if isfile(DPKG_STATUS_FILE):
            dpkg_status = True

        # make the file names
        olu_file = '/tmp/' + new_oresat_file(keyword=OLU_STATUS_KEYWORD)
        olu_tar = '/tmp/' + new_oresat_file(keyword=OLU_STATUS_KEYWORD, ext='.tar.xz')
        if dpkg_status:
            dpkg_file = new_oresat_file(keyword=DPKG_STATUS_KEYWORD)

        with open(olu_file, 'w') as f:
            f.write(json.dumps(listdir(self._cache_dir)))

        with tarfile.open(olu_tar, 'w:xz') as t:
            t.add(olu_file, arcname=basename(olu_file))
            if dpkg_status:
                t.add(DPKG_STATUS_FILE, arcname=basename(dpkg_file))

        remove(olu_file)

        return olu_tar

    @property
    def status(self) -> UpdaterState:
        '''UpdaterState: The current state.'''

        return self._state

    @property
    def updates_cached(self) -> int:
        '''int: The number of update archives in cache.'''

        return len(self._cache)

    @property
    def list_updates(self) -> str:
        '''str: Get a JSON list of file_name in cache.'''

        return json.dumps(self._cache)

    @property
    def update_archive(self) -> str:
        '''str: Current update archive while updating.'''

        return self._update_archive

    @property
    def total_instructions(self) -> int:
        '''int: The total number of instructions in the update running.'''

        return self._total_instructions

    @property
    def instruction_index(self) -> int:
        '''int: The index of the instruction currently running.'''

        return self._instruction_index

    @property
    def instruction_percent(self) -> int:
        '''int: The percentage of the instructions completed.'''

        return self._instruction_percent

    @property
    def instruction_command(self) -> str:
        '''str: The current bash command being running.'''

        return self._command


def is_update_archive(file_path: str) -> bool:
    '''Check to see if the input is a valid update archive.

    Parameters
    ----------
    file_path: str
        Path to the update archive.

    Returns
    -------
    bool
        True the file name is valid or False if it is invalid.
    '''

    try:
        oresat_file = OreSatFile(file_path)
    except Exception:
        return False

    if oresat_file.keyword == 'update' and oresat_file.extension == '.tar.xz':
        return True

    return False
