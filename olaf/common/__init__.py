"""Common OLAF class and functions."""

import re


def natsorted(data: list[str], ignore_case: bool = False) -> list[str]:
    """
    Sort a list with natural sort.

    Parameters
    ----------
    data: list[str]
        List of strings to sort.
    ignore_case: bool
        Set to True to ignore case

    Returns
    -------
    list[str]
        List of natural sorted strings.
    """

    convert = lambda text: int(text) if text.isdigit() else (text.lower() if ignore_case else text)
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(data, key=alphanum_key)
