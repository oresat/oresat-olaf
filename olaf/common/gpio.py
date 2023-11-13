"""Quick GPIO legacy sysfs wrapper that supports mocking."""

import os

GPIO_LOW = 0
"""int: GPIO pin value is low"""
GPIO_HIGH = 1
"""int: GPIO pin value is high"""
GPIO_IN = "in"
"""str: GPIO pin is a input"""
GPIO_OUT = "out"
"""str: GPIO pin is a output"""


class GpioError(Exception):
    """Error with :py:class:`Gpio`"""


class Gpio:
    """
    Quick GPIO legacy sysfs wrapper class that can handle issues with gpio pin on the OreSat cards
    when those pins are configured with device tree and/or device tree overlays.

    Also supports mocking.
    """

    _GPIO_DIR_PATH = "/sys/class/gpio"

    _LABELS = {}
    if os.path.isdir(_GPIO_DIR_PATH):
        for i in os.listdir(_GPIO_DIR_PATH):
            if i.startswith("gpiochip") or i in ["export", "unexport"]:
                continue
            with open(f"{_GPIO_DIR_PATH}/{i}/label", "r") as f:
                _LABELS[f.read()[:-1]] = int(i[4:])  # remove the trailing '\n'

    def __init__(self, pin: str, mock: bool = False):
        """
        Parameters
        ----------
        pin: str or int
            The GPIO name/label defined by device tree or the pin number. The name from the device
            tree is the preferred value.
        mock: bool
            Mock the GPIO.
        """

        self._mock = mock

        # defaults
        self._pin = 0
        self._mock_value = 0
        self._name = "MOCKED"
        self._mode = GPIO_OUT

        if isinstance(pin, int):
            self._pin = pin
        elif isinstance(pin, str):
            if mock:
                self._name = pin
            else:
                self._pin = self._LABELS[pin]
        else:
            raise GpioError(f"invalid pin {pin}")

        self._gpio_dir_path = f"{self._GPIO_DIR_PATH}/gpio{self._pin}"

        if not self._mock:
            if not os.path.isdir(self._gpio_dir_path):
                raise GpioError(f"gpio pin {self._name} (gpio{self._pin}) does not exist")

            with open(f"{self._gpio_dir_path}/direction", "r") as f:
                self._mode = f.read()
            with open(f"{self._gpio_dir_path}/label", "r") as f:
                self._name = f.read()

    @property
    def mode(self) -> str:
        """str: The GPIO pin mode. Readwrite."""

        return self._mode

    @mode.setter
    def mode(self, new_mode: str):
        if new_mode == self._mode:
            return  # already in the correct mode

        if not self._mock:
            with open(f"{self._gpio_dir_path}/direction", "w") as f:
                f.write(new_mode)
        self._mode = new_mode

    @property
    def value(self) -> int:
        """bool: The value of GPIO pin. Readwrite."""

        if self._mock:
            return self._mock_value

        with open(f"{self._gpio_dir_path}/value", "r") as f:
            value = int(f.read())

        return value

    @value.setter
    def value(self, new_value: int):
        if self._mode == "in":
            raise GpioError(f"Cannot set GPIO {self.number} value, it is in input mode")

        if self._mock:
            self._mock_value = new_value
        else:
            with open(f"{self._gpio_dir_path}/value", "w") as f:
                f.write(str(new_value))

    def high(self):
        """Set the GPIO high."""

        self.value = 1

    def low(self):
        """Set the GPIO low."""

        self.value = 0

    @property
    def is_high(self) -> bool:
        """bool: Check if the GPIO is set high. Readonly."""

        return bool(self.value)

    @property
    def number(self) -> int:
        """int: The GPIO number. Readonly."""

        return self._pin

    @property
    def name(self) -> str:
        """str: The GPIO name/label. Readonly."""

        return self._name
