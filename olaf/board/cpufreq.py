"""Functions to get/set the CPU frequency and its governor on the Octavo A8."""

from os import geteuid

from loguru import logger

A8_CPUFREQS = [300, 600, 720, 800, 1000]
"""list: CPU frequencies for the Cortex A8 in MHz"""

_CPU0_PATH = "/sys/devices/system/cpu/cpufreq/policy0"


def get_cpufreq() -> int:
    """
    Get the current CPU frequency.

    Returns
    -------
    int
        The current cpufreq in MHz.
    """

    with open(f"{_CPU0_PATH}/scaling_cur_freq", "r") as f:
        value = int(f.read()) // 1000
    return value


def set_cpufreq(value: int):
    """
    Set the current CPU frequency. Must be running as root to use this function.

    Parameters
    ----------
    value: int
        The cpufreq in MHz to change to. Must be a value from :py:data:`A8_CPUFREQS`.
    """

    if geteuid() != 0:  # not running as root
        logger.warning("cannot set cpufreq, not running at root")
        return
    if value not in A8_CPUFREQS:
        logger.warning(f"invalid cpufreq of {value} MHz")
        return

    with open(f"{_CPU0_PATH}/scaling_setspeed", "w") as f:
        f.write(str(value * 1000))


def get_cpufreq_gov() -> str:
    """
    Get the current cpu governor; ether ``"performance"`` or ``"powersave"``.

    Returns
    -------
    str
        The current CPU governor.
    """

    with open(f"{_CPU0_PATH}/scaling_governor", "r") as f:
        gov = f.read().strip()

    return gov


def set_cpufreq_gov(cpufreq_gov: str):
    """
    Set the current cpu governor.

    Parameters
    -------
    cpufreq_gov: CpuGovenor
        The CPU governor to change to. Must be ``"performance"`` or ``"powersave"``
    """

    if geteuid() != 0:  # not running as root
        logger.warning("cannot set cpufreq governor, not running at root")
        return
    if cpufreq_gov not in ["performance", "powersave"]:
        logger.warning(f"invalid cpufreq governor of {cpufreq_gov}")
        return

    with open(f"{_CPU0_PATH}/scaling_governor", "w") as f:
        f.write(cpufreq_gov)
