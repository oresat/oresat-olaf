import os


class GPIOError(Exception):
    '''Error with GPIO'''


class GPIO:
    '''
    Quick GPIO class that can handles the GPIO export file raising an error on the A8 (when the
    export actually works). Only support GPIO outputs.

    On OreSat boards, it's common for a single GPIO output to control powering on or off the
    board specific hardware.

    Also supports mocking.
    '''

    def __init__(self, number: int, mock: bool = False):
        '''
        Parameters
        ----------
        number: int
            The GPIO number.
        mock: bool
            Mock the GPIO.
        '''

        self._number = number
        self._is_high = False  # save on IO calls
        self._mock = mock

        if not self._mock:
            if not os.path.isdir(f'/sys/class/gpio/gpio{self._number}'):
                raise GPIOError(f'gpio{number} does not exist')

            try:
                with open('/sys/class/gpio/export', 'w') as f:
                    f.write(str(self._number))
                with open('/sys/class/gpio/export', 'w') as f:
                    f.write(str(self._number))
            except PermissionError:
                pass  # will always fail, tho it actually works

            with open(f'/sys/class/gpio/gpio{self._number}/direction', 'w') as f:
                f.write('out')

            with open(f'/sys/class/gpio/gpio{self._number}/value', 'r') as f:
                self._is_high = f.read() == '1'

    def high(self):
        '''Set the GPIO high.'''

        if self._is_high:
            return  # already on

        if not self._mock:
            with open(f'/sys/class/gpio/gpio{self._number}/value', 'w') as f:
                f.write('1')

        self._is_high = True

    def low(self):
        '''Set the GPIO low.'''

        if not self._is_high:
            return  # already off

        if not self._mock:
            with open(f'/sys/class/gpio/gpio{self._number}/value', 'w') as f:
                f.write('0')

        self._is_high = False

    @property
    def is_high(self) -> bool:
        '''bool: Check if the GPIO is set high.'''

        return self._is_high

    @property
    def number(self):
        '''int: The GPIO number'''

        return self._number
