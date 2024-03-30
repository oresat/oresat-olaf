"""Common OLAF class and functions."""

import re


def natsorted(data: list[str], ignore_case: bool = False) -> list[str]:
    """Sort a list with natural sort. Option to ignore case as well."""

    # pylint: disable=unnecessary-lambda-assignment
    convert = lambda text: int(text) if text.isdigit() else (text.lower() if ignore_case else text)
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(data, key=alphanum_key)
