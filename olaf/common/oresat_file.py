"""File name format for OreSat files"""
from __future__ import annotations

from pathlib import Path
from os import uname
from os.path import basename
from time import time


def new_oresat_file(keyword: str, card: str = "", date: float = -1.0, ext: str = "") -> str:
    """
    Convenience function for making valid oresat file_names

    Parameters
    ----------
    keyword: str
        The keyword for the new file_name
    card: str
        The card name for the file_name. If not set, the hostname will be
        used.
    date: float
        Unix timestamp the file was made. Set to a :py:func:`time.time` value or set to a negative
        number to use current time.
    ext: str
        The file extension. Optional.

    Returns
    -------
    str
        The new oresat file name.
    """

    if not card:
        card = uname().nodename
    card = card.removeprefix('oresat-')

    if date < 0:
        date = time()
    date = int(date * 1000)

    # make sure the extension starts with a '.'
    if ext and not ext.startswith("."):
        ext = "." + ext

    return f'{card}_{keyword}_{date}{ext}'.lower()


class OreSatFile:
    """A class that follows the OreSat file format."""

    def __init__(self, file: str | Path) -> None:
        """
        Parameters
        ----------
        file_name: str
            Name of the OreSat file.

        Raises
        ------
        ValueError
            If file name format is wrong.
        """

        self._name = basename(file)

        split = self._name.split("_")
        if len(split) != 3:
            raise ValueError("invalid OreSat file name")

        self._card = split[0]
        self._keyword = split[1]
        temp = split[2]

        if not self._card or not self._keyword or not temp:
            raise ValueError("invalid OreSat file name")

        if "." in temp:
            self._date = float(temp.split(".")[0]) / 1000
            self._extension = temp[temp.find(".") :]
        else:
            self._date = float(temp) / 1000
            self._extension = ""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self._name}"

    def __str__(self) -> str:
        return self._name

    def __lt__(self, other: 'OreSatFile') -> bool:
        return self._date < other.date

    def __gt__(self, other: 'OreSatFile') -> bool:
        return self._date > other.date

    @property
    def name(self) -> str:
        """str: The name of the file. Read only."""

        return self._name

    @property
    def card(self) -> str:
        """str: The card the file is for or the card the file was made on. Read only."""

        return self._card
    
    @property
    def card_underscore(self) -> str:
        """str: The card the file is for, but in the format expected by OreSatConfigs. Read only."""

        return self.card.replace("-","_")

    @property
    def keyword(self) -> str:
        """str: The keyword for the file, this can be used to figure out what todo with the
        file. Read only."""

        return self._keyword

    @property
    def date(self) -> float:
        """float: The Unix time the file was made in milliseconds. Read only."""

        return self._date

    @property
    def extension(self) -> str:
        """str: The file extension. Can be an empty string. Read only."""

        return self._extension
