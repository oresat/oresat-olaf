"""Small class to abstract the Octavo A8 ADC pins"""

import os


class AdcError(Exception):
    """Error with Adc"""


class Adc:
    """Octavo A8 ADC pin"""

    ADC_VIN = 1.8  # volts
    ADC_BITS = 12
    ADC_MAX_VALUE = (2**ADC_BITS) - 1

    def __init__(self, pin: int, mock: bool = False):
        """
        Parameters
        ----------
        pin: int
            The pin number between 0 and 7 for the adc pin on the Octavo A8.
        mock: bool
            Mock the ADC.
        """

        self._mock = mock
        self._mock_value = self.ADC_MAX_VALUE // 2

        if not isinstance(pin, int) or pin < 0 or pin > 7:
            raise AdcError(f"invalid pin number {pin}, must be between 0 and 7")

        self.pin = pin
        self._adc_path = f"/sys/bus/iio/devices/iio:device0/in_voltage{pin}_raw"

    @property
    def raw(self) -> int:
        """int: The raw value from the ADC"""

        if self._mock:
            return self._mock_value

        if not os.path.isfile(self._adc_path):
            raise AdcError(f"could not find ADC file {self._adc_path}")

        with open(self._adc_path, "r") as f:
            value = int(f.read())

        return value

    @property
    def value(self) -> float:
        """float: The ADC voltage value in volts."""

        return (self.raw / self.ADC_MAX_VALUE) * self.ADC_VIN
