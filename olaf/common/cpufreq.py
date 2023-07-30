'''Functions to get/set the CPU frequency and its governor on the Octavo A8.'''

from os import geteuid

A8_CPUFREQS = [300, 600, 720, 800, 1000]
'''list: CPU frequencies for the Cortex A8 in MHz'''


def get_cpufreq() -> int:
    '''
    Get the current CPU frequency.

    Returns
    -------
    int
        The current cpufreq in MHz.
    '''

    with open('/sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq', 'r') as f:
        value = int(f.read()) // 1000
    return value


def set_cpufreq(value: int):
    '''
    Set the current CPU frequency. Must be running as root to use this function.

    Parameters
    ----------
    value: int
        The cpufreq in MHz to change to. Must be a value from :py:data:`A8_CPUFREQS`.
    '''

    if geteuid() != 0:  # not running as root
        raise PermissionError('cannot set cpufreq, not running at root')
    if value not in A8_CPUFREQS:
        raise ValueError(f'invalid cpufreq of {value} MHz')

    with open('/sys/devices/system/cpu/cpufreq/policy0/scaling_setspeed', 'w') as f:
        f.write(str(value * 1000))


def get_cpufreq_gov() -> str:
    '''
    Get the current cpu governor; ether ``'performace'`` or ``'powesave'``.

    Returns
    -------
    str
        The current CPU governor.
    '''

    with open('/sys/devices/system/cpu/cpufreq/policy0/scaling_governor', 'r') as f:
        gov = f.read().strip()

    return gov


def set_cpufreq_gov(cpufreq_gov: str):
    '''
    Set the current cpu governor.

    Parameters
    -------
    cpufreq_gov: CpuGovenor
        The CPU governor to change to. Must be ``'performace'`` or ``'powesave'``
    '''

    with open('/sys/devices/system/cpu/cpufreq/policy0/scaling_governor', 'w') as f:
        f.write(cpufreq_gov.value)
