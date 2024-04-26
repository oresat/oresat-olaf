"""ECSS Space engineering CANbus extension protocol

SCET definition:

struct {
    unsigned 32 Coarse Time
    unsigned 24 Fine Time (sub seconds)
} SCET


UTC definition:

struct {
    unsigned 16 Day
    unsigned 32 ms of day
    unsigned 16 submilliseconds of ms
} UTC
"""


def scet_int_from_time(unix_time: float) -> int:
    """Convert a float to SCET int

    Parameters
    ----------
    unix_time: float
        time in the :py:func:`time.time` format

    Returns
    -------
    int
        unix_time to convert to SCET time as a int
    """

    coarse = int(unix_time)
    coarse_bytes = coarse.to_bytes(4, "little")
    fine = int(unix_time % 1 * 1000000)
    fine_bytes = fine.to_bytes(4, "little")

    raw = coarse_bytes + fine_bytes[:3] + b"\x00"

    return int.from_bytes(raw, "little")


def scet_int_to_time(scet: int) -> float:
    """Convert a SCET int to :py:func:`time.time()` format

    Parameters
    ----------
    scet: int
        SCET time as a int

    Returns
    -------
    float
        time in the :py:func:`time.time` format
    """

    raw = scet.to_bytes(8, "little")

    coarse = int.from_bytes(raw[:4], "little")
    fine = int.from_bytes(raw[4:-1], "little")

    return coarse + fine / 1000000


def utc_int_from_time(unix_time: float) -> int:
    """Convert a float to ECSS UTC int

    Parameters
    ----------
    unix_time: float
        time in the :py:func:`time.time` format

    Returns
    -------
    int
        unix_time to convert to ECSS UTC time as a int
    """

    day = int(unix_time / 86400)
    temp_us = unix_time % 86400 * 1000000
    ms_of_day = int(temp_us / 1000)
    us_of_day = int(temp_us % 1000)

    day_bytes = day.to_bytes(2, "little")
    ms_of_day_bytes = ms_of_day.to_bytes(4, "little")
    us_of_day_bytes = us_of_day.to_bytes(2, "little")

    raw = day_bytes + ms_of_day_bytes + us_of_day_bytes

    return int.from_bytes(raw, "little")


def utc_int_to_time(utc: int) -> float:
    """Convert a ECSS UTC int to :py:func:`time.time()` format

    Parameters
    ----------
    scet: int
        ECSS UTC time as a int

    Returns
    -------
    float
        time in the :py:func:`time.time` format
    """

    raw = utc.to_bytes(8, "little")

    day = int.from_bytes(raw[:2], "little")
    ms_of_day = int.from_bytes(raw[2:-2], "little")
    us_of_day = int.from_bytes(raw[-2:], "little")

    return day * 86400 + ms_of_day / 1000 + us_of_day / 1000000
