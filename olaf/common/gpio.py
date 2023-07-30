'''Quick GPIO legacy sysfs wrapper that supports mocking.'''

import os


GPIO_LOW = 0
'''int: GPIO pin value is low'''
GPIO_HIGH = 1
'''int: GPIO pin value is high'''
GPIO_IN = 'in'
'''int: GPIO pin is a input'''
GPIO_OUT = 'out'
'''int: GPIO pin is a output'''


class GpioError(Exception):
    '''Error with :py:class:`Gpio`'''


class Gpio:
    '''
    Quick GPIO legacy sysfs wrapper class that can handle issue with gpio pin on the Octavo A8 when
    those pins are configured with device tree overlays.

    On OreSat cards the GPIO pins don't always work nicely with common Python legacy GPIO
    libraries. This class can handle the GPIO export file raising an error on the A8 (when the
    export actually works) and also works when export is not needed at all.

    Also supports mocking.
    '''

    def __init__(self, number: int, mock: bool = False, mode: str = 'out', export: bool = True):
        '''
        Parameters
        ----------
        number: int
            The GPIO number.
        mock: bool
            Mock the GPIO.
        mode: str
            The default mode for the pin. Must be ``'in'`` or ``'out'``.
        export: bool
            Export the gpio pin before puting it the mode.
        '''
        # default values and order is for backwards compatibility

        self._number = number
        self._mock = mock
        self._gpio_dir_path = f'/sys/class/gpio/gpio{self._number}'
        self._gpio_export_path = '/sys/class/gpio/export'

        if self._mock:
            self._mock_value = 0
        else:
            if not os.path.isdir(self._gpio_dir_path):
                raise GpioError(f'gpio{number} does not exist')

            if export:
                self.export()

            with open(f'{self._gpio_dir_path}/direction', 'r') as f:
                cur_mode = f.read()
            if cur_mode != mode:
                with open(f'{self._gpio_dir_path}/direction', 'w') as f:
                    f.write(mode)

        self._mode = mode  # save on IO calls

    def export(self):
        '''Export the pin'''

        try:
            with open('/sys/class/gpio/export', 'w') as f:
                f.write(str(self._number))
            with open('/sys/class/gpio/export', 'w') as f:
                f.write(str(self._number))
        except PermissionError:
            pass  # will always fail the first time

    def unexport(self):
        '''Unexport the pin'''

        try:
            with open('/sys/class/gpio/unexport', 'w') as f:
                f.write(str(self._number))
        except PermissionError:
            pass  # will always fail the first time

        with open('/sys/class/gpio/unexport', 'w') as f:
            f.write(str(self._number))

    @property
    def mode(self) -> str:
        '''str: The GPIO pin mode. Readwrite.'''

        return self._mode

    @mode.setter
    def mode(self, new_mode: str):

        if new_mode == self._mode:
            return  # already in the correct mode

        if not self._mock:
            with open(f'{self._gpio_dir_path}/direction', 'w') as f:
                f.write(new_mode)
        self._mode = new_mode

    @property
    def value(self) -> int:
        '''bool: The value of GPIO pin. Readwrite.'''

        if self._mock:
            return self._mock_value

        with open(f'{self._gpio_dir_path}/value', 'r') as f:
            value = int(f.read())

        return value

    @value.setter
    def value(self, new_value: int):

        if self._mode == 'in':
            raise GpioError(f'Cannot set GPIO{self._number} value, it is in input mode')

        if self._mock:
            self._mock_value = new_value
        else:
            with open(f'{self._gpio_dir_path}/value', 'w') as f:
                f.write(str(new_value))

    def high(self):
        '''Set the GPIO high.'''

        self.value = 1

    def low(self):
        '''Set the GPIO low.'''

        self.value = 0

    @property
    def is_high(self) -> bool:
        '''bool: Check if the GPIO is set high. Readonly.'''

        return bool(self.value)

    @property
    def number(self) -> int:
        '''int: The GPIO number. Readonly.'''

        return self._number
