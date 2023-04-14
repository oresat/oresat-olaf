from os import geteuid

A8_CPUFREQS = [300, 600, 720, 800, 1000]
'''CPU frequencies for the Cortex A8 in MHz'''


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
    Set the current CPU frequency.

    Note: The values for Cortex A8 are 300, 600, 720, 800, and 1000.

    Parameters
    ----------
    value: int
        The cpufreq in MHz to change to.
    '''

    if geteuid() != 0:  # not running as root
        raise PermissionError('cannot set cpufreq, not running at root')
    if value not in A8_CPUFREQS:
        raise ValueError(f'cannot set cpufreq to {value}, valid values are {A8_CPUFREQS}')

    with open('/sys/devices/system/cpu/cpufreq/policy0/scaling_setspeed', 'w') as f:
        f.write(str(value * 1000))


def get_cpufreq_gov() -> str:
    '''
    Get the current cpu governor.

    Returns
    -------
    str
        The current CPU  governor.
    '''

    with open('/sys/devices/system/cpu/cpufreq/policy0/scaling_governor', 'r') as f:
        value = f.read().strip()
    return value
