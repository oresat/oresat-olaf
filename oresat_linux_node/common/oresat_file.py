'''File name format for OreSat files'''

from os import uname
from os.path import basename
from time import time


def new_oresat_file(keyword: str, board: str = '', date: float = -1.0, ext: str = '') -> str:
    '''Convience function for making valid oresat file_names

    Parameters
    ----------
    keyword: str
        The keyword for the new file_name
    board: str
        The board name for the file_name. If not set, the hostname will be
        used.
    date: Union(None, float)
        Unix timestamp the file was made. Set to a :py:func:`time.time` value or set to a negative
        number to use current time.
    ext: str
        The file extension. Optional.

    Returns
    -------
    str
        The new oresat file name.
    '''

    if not board:
        board = uname()[1]

    if date < 0:
        date_str = str(int(time()))
    else:
        date_str = str(int(date))

    # make sure the extension starts with a '.'
    if len(ext) > 0 and ext[0] != '.':
        ext = '.' + ext

    name = board + '_' + keyword + '_' + date_str + ext

    return name.lower()


class OreSatFile:
    '''A class that follows the OreSat file format.'''

    def __init__(self, file: str):
        '''
        Parameters
        ----------
        file_name: str
            Name of the OreSat file.

        Raises
        ------
        ValueError
            If file name format is wrong.
        '''

        self._name = basename(file)

        split = self._name.split('_')
        if len(split) != 3:
            raise ValueError('invalid OreSat file name')

        self._board = split[0]
        self._keyword = split[1]
        temp = split[2]

        if not self._board or not self._keyword or not temp:
            raise ValueError('invalid OreSat file name')

        if '.' in temp:
            self._date = float(temp.split('.')[0])
            self._extension = temp[temp.find('.'):]
        else:
            self._date = float(temp)
            self._extension = ''

    def __repr__(self):

        return '{} {}'.format(self.__class__.__name__, self._name)

    def __str__(self):

        return self._name

    def __lt__(self, archive_file2):

        return self._date < archive_file2.date

    def __gt__(self, archive_file2):

        return self._date > archive_file2.date

    @property
    def name(self) -> str:
        '''str: The name of the file. Read only.'''

        return self._name

    @property
    def board(self) -> str:
        '''str: The board the file is for or the board the file was made on. Read only.'''

        return self._board

    @property
    def keyword(self) -> str:
        '''str: The keyword for the file, this can be used to figure out what todo with the
        file. Read only.'''

        return self._keyword

    @property
    def date(self) -> float:
        '''float: The Unix time the file was made. Read only.'''

        return self._date

    @property
    def extension(self) -> str:
        '''str: The file extension. Can be an empty string. Read only.'''

        return self._extension
