"""Common OLAF class and functions."""

from __future__ import annotations

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

    if not data:
        return []

    def convert(text: str) -> int | str:
        if text.isdigit():
            return int(text)
        if ignore_case:
            return text.lower()
        return text

    def alphanum_key(key: str) -> list[int | str]:
        return [convert(c) for c in re.split("([0-9]+)", str(key))]

    return sorted(data, key=alphanum_key)
