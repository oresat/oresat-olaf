'''Small class to abstract the Octavo A8 ADC pins'''

import os


class AdcError(Exception):
    '''Error with Adc'''


class Adc:
    '''Octavo A8 ADC pin'''

    ADC_VIN = 1.8  # volts
    ADC_BITS = 12
    ADC_MAX_VALUE = (2 ** ADC_BITS) - 1

    def __init__(self, pin: int):
        '''
        Parameters
        ----------
        int: int
            THe pin number between 0 and 7 for the adc pin on the Octavo A8.
        '''

        if pin < 0 or pin > 7:
            raise AdcError(f'Invalid pin number {pin}, must be between 0 and 7')

        self.pin = pin
        self._adc_path = f'/sys/bus/iio/devices/iio:device0/in_voltage{pin}_raw'

    @property
    def raw(self) -> int:
        '''int: the raw value from the ADC'''

        if not os.path.isfile(self._adc_path):
            raise AdcError(f'could not find ADC file {self._adc_path}')

        with open(self._adc_path, 'r') as f:
            value = int(f.read)

        return value

    @property
    def value(self) -> float:
        '''float: The value from the ADC adjusted for the voltage'''

        return (self.raw / self.ADC_MAX_VALUE) * self.ADC_VIN