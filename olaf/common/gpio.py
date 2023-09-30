'''Quick GPIO legacy sysfs wrapper that supports mocking.'''

import os
from enum import IntEnum


GPIO_LOW = 0
'''int: GPIO pin value is low'''
GPIO_HIGH = 1
'''int: GPIO pin value is high'''
GPIO_IN = 'in'
'''str: GPIO pin is a input'''
GPIO_OUT = 'out'
'''str: GPIO pin is a output'''


def gpio_signal_to_num(chip: int, num: int) -> int:
    '''Convert GPIO signal name values (chip and pin numbers) to system gpio number.'''
    return chip * 32 + num


class GpioPin(IntEnum):
    '''GPIO pins for the AM335x'''

    # CHIP 0
    MDIO = gpio_signal_to_num(0, 0)
    MDC = gpio_signal_to_num(0, 1)
    SPI0_SLCK = gpio_signal_to_num(0, 2)
    SPI0_D0 = gpio_signal_to_num(0, 3)
    SPI0_D1 = gpio_signal_to_num(0, 4)
    SPI0_CS0 = gpio_signal_to_num(0, 5)
    SPI0_CS1 = gpio_signal_to_num(0, 6)
    ECAP0_IN_PWM0_OUT = gpio_signal_to_num(0, 7)
    LCD_DATA12 = gpio_signal_to_num(0, 8)
    LCD_DATA13 = gpio_signal_to_num(0, 9)
    LCD_DATA14 = gpio_signal_to_num(0, 10)
    LCD_DATA15 = gpio_signal_to_num(0, 11)
    UART1_CTSN = gpio_signal_to_num(0, 12)
    UART1_RTSN = gpio_signal_to_num(0, 13)
    UART1_RXD = gpio_signal_to_num(0, 14)
    UART1_TXD = gpio_signal_to_num(0, 15)
    MII1_TXD3 = gpio_signal_to_num(0, 16)
    MII1_TXD2 = gpio_signal_to_num(0, 17)
    USB0_DRVVBUS = gpio_signal_to_num(0, 18)
    XDMA_EVENT_INTR0 = gpio_signal_to_num(0, 19)
    XDMA_EVENT_INTR1 = gpio_signal_to_num(0, 20)
    MII1_TXD1 = gpio_signal_to_num(0, 21)
    GPMC_AD8 = gpio_signal_to_num(0, 22)
    GPMC_AD9 = gpio_signal_to_num(0, 23)
    # no gpio0_24 or gpio0_25
    GPMC_AD10 = gpio_signal_to_num(0, 26)
    GPMC_AD11 = gpio_signal_to_num(0, 27)
    MII1_TXD0 = gpio_signal_to_num(0, 28)
    RMII1_REF_CLK = gpio_signal_to_num(0, 29)
    GPMC_WAIT0 = gpio_signal_to_num(0, 30)
    GPMC_WPN = gpio_signal_to_num(0, 31)
    # CHIP 1
    GPMC_AD0 = gpio_signal_to_num(1, 0)
    GPMC_AD1 = gpio_signal_to_num(1, 1)
    GPMC_AD2 = gpio_signal_to_num(1, 2)
    GPMC_AD3 = gpio_signal_to_num(1, 3)
    GPMC_AD4 = gpio_signal_to_num(1, 4)
    GPMC_AD5 = gpio_signal_to_num(1, 5)
    GPMC_AD6 = gpio_signal_to_num(1, 6)
    GPMC_AD7 = gpio_signal_to_num(1, 7)
    UART0_CTSN = gpio_signal_to_num(1, 8)
    UART0_RTSN = gpio_signal_to_num(1, 9)
    UART0_RXD = gpio_signal_to_num(1, 10)
    UART0_TXD = gpio_signal_to_num(1, 11)
    GPMC_AD12 = gpio_signal_to_num(1, 12)
    GPMC_AD13 = gpio_signal_to_num(1, 13)
    GPMC_AD14 = gpio_signal_to_num(1, 14)
    GPMC_AD15 = gpio_signal_to_num(1, 15)
    GPMC_A0 = gpio_signal_to_num(1, 16)
    GPMC_A1 = gpio_signal_to_num(1, 17)
    GPMC_A2 = gpio_signal_to_num(1, 18)
    GPMC_A3 = gpio_signal_to_num(1, 19)
    GPMC_A4 = gpio_signal_to_num(1, 20)
    GPMC_A5 = gpio_signal_to_num(1, 21)
    GPMC_A6 = gpio_signal_to_num(1, 22)
    GPMC_A7 = gpio_signal_to_num(1, 23)
    GPMC_A8 = gpio_signal_to_num(1, 24)
    GPMC_A9 = gpio_signal_to_num(1, 25)
    GPMC_A10 = gpio_signal_to_num(1, 26)
    GPMC_A11 = gpio_signal_to_num(1, 27)
    GPMC_BEN1 = gpio_signal_to_num(1, 28)
    GPMC_CSN0 = gpio_signal_to_num(1, 29)
    GPMC_CSN1 = gpio_signal_to_num(1, 30)
    GPMC_CSN2 = gpio_signal_to_num(1, 31)
    # CHIP 2
    GPMC_CSN3 = gpio_signal_to_num(2, 0)
    GPMC_CLK = gpio_signal_to_num(2, 1)
    GPMC_ADCN_ALE = gpio_signal_to_num(2, 2)
    GPMC_OEN_REN = gpio_signal_to_num(2, 3)
    GPMC_WEN = gpio_signal_to_num(2, 4)
    GPMC_BEN0_CLE = gpio_signal_to_num(2, 5)
    LCD_DATA0 = gpio_signal_to_num(2, 6)
    LCD_DATA1 = gpio_signal_to_num(2, 7)
    LCD_DATA2 = gpio_signal_to_num(2, 8)
    LCD_DATA3 = gpio_signal_to_num(2, 9)
    LCD_DATA4 = gpio_signal_to_num(2, 10)
    LCD_DATA5 = gpio_signal_to_num(2, 11)
    LCD_DATA6 = gpio_signal_to_num(2, 12)
    LCD_DATA7 = gpio_signal_to_num(2, 13)
    LCD_DATA8 = gpio_signal_to_num(2, 14)
    LCD_DATA9 = gpio_signal_to_num(2, 15)
    LCD_DATA10 = gpio_signal_to_num(2, 16)
    LCD_DATA11 = gpio_signal_to_num(2, 17)
    MII1_RXD3 = gpio_signal_to_num(2, 18)
    MII1_RXD2 = gpio_signal_to_num(2, 19)
    MII1_RXD1 = gpio_signal_to_num(2, 20)
    MII1_RXD0 = gpio_signal_to_num(2, 21)
    LCD_VSYNC = gpio_signal_to_num(2, 22)
    LCD_HSYNC = gpio_signal_to_num(2, 23)
    LCD_PCLK = gpio_signal_to_num(2, 24)
    LCD_AC_BIAS_EN = gpio_signal_to_num(2, 25)
    MMC0_DAT3 = gpio_signal_to_num(2, 26)
    MMC0_DAT2 = gpio_signal_to_num(2, 27)
    MMC0_DAT1 = gpio_signal_to_num(2, 28)
    MMC0_DAT0 = gpio_signal_to_num(2, 29)
    MMC0_CLK = gpio_signal_to_num(2, 30)
    MMC0_CMD = gpio_signal_to_num(2, 31)
    # CHIP 3
    MII1_COL = gpio_signal_to_num(3, 0)
    MII1_CRS = gpio_signal_to_num(3, 1)
    MII1_RX_ER = gpio_signal_to_num(3, 2)
    MII1_TX_EN = gpio_signal_to_num(3, 3)
    MII1_RX_DV = gpio_signal_to_num(3, 4)
    I2C0_SDA = gpio_signal_to_num(3, 5)
    I2C0_SCL = gpio_signal_to_num(3, 6)
    EMU0 = gpio_signal_to_num(3, 7)
    EMU1 = gpio_signal_to_num(3, 8)
    MII1_TX_CLK = gpio_signal_to_num(3, 9)
    MII1_RX_CLK = gpio_signal_to_num(3, 10)
    # no gpio3_11 or gpio3_12
    USB1_DRVVBUS = gpio_signal_to_num(3, 13)
    MCASP0_ACLKX = gpio_signal_to_num(3, 14)
    MCASP0_FSX = gpio_signal_to_num(3, 15)
    MCASP0_AXR0 = gpio_signal_to_num(3, 16)
    MCASP0_AHCLKR = gpio_signal_to_num(3, 17)
    MCASP0_ACLKR = gpio_signal_to_num(3, 18)
    MCASP0_FSR = gpio_signal_to_num(3, 19)
    MCASP0_AXR1 = gpio_signal_to_num(3, 20)
    MCASP0_AHCLKX = gpio_signal_to_num(3, 21)
    # no gpio3_22 thru gpio3_31

    @property
    def signal_name(self) -> str:
        '''str: The gpio signal name in ``"gpioA_B"`` format.'''
        return f'gpio{self.value // 32}_{self.value % 32}'


class GpioError(Exception):
    '''Error with :py:class:`Gpio`'''


class Gpio:
    '''
    Quick GPIO legacy sysfs wrapper class that can handle issue with gpio pin on the Octavo A8 when
    those pins are configured with device tree overlays.

    On OreSat cards the GPIO pins don't always work nicely with common Python legacy GPIO
    libraries. This class can handle the GPIO export file raising an error on the A8 (when the
    export actually works) and also works when export is not needed at all (pin mode and direction
    is configured by device tree).

    Also supports mocking.
    '''

    _GPIO_DIR_PATH = '/sys/class/gpio'

    _LABELS = {}
    if os.path.isdir(_GPIO_DIR_PATH):
        for i in os.listdir(_GPIO_DIR_PATH):
            if i.startswith('gpiochip') or i in ['export', 'unexport']:
                continue
            with open(f'{_GPIO_DIR_PATH}/{i}/label', 'r') as f:
                name = f.read()[:-1]  # remove the trailing '\n'
                _LABELS[name] = int(i[4:])

    def __init__(self, pin: str, mock: bool = False, mode: str = 'out', export: bool = True):
        '''
        Parameters
        ----------
        pin: GpioPin, int, str
            The pin name, GPIO pin number, or GPIO name/label defined by device tree.
        mock: bool
            Mock the GPIO.
        mode: str
            The default mode for the pin. Use ``GPIO_IN`` or ``GPIO_OUT``.
        export: bool
            Export the gpio pin before puting it the mode.
        '''
        # default values and order is for backwards compatibility

        self._mock = mock

        # defaults
        self._pin = 0
        self._mock_value = 0
        self._name = 'MOCKED'

        if isinstance(pin, GpioPin):
            self._pin = pin.value
        elif isinstance(pin, int):
            self._pin = pin
        elif isinstance(pin, str):
            if mock:
                self._name = pin
            else:
                self._pin = self._LABELS[pin]
        else:
            raise GpioError(f'invalid pin {pin}')

        self._gpio_dir_path = f'{self._GPIO_DIR_PATH}/gpio{self._pin}'

        if not self._mock:
            if not os.path.isdir(self._gpio_dir_path):
                raise GpioError(f'gpio pin {self._name} (gpio{self._pin}) does not exist')

            if export:
                self.export()

            with open(f'{self._gpio_dir_path}/direction', 'r') as f:
                cur_mode = f.read()
            if cur_mode != mode:
                with open(f'{self._gpio_dir_path}/direction', 'w') as f:
                    f.write(mode)
            with open(f'{self._gpio_dir_path}/label', 'r') as f:
                self._name = f.read()

        self._mode = mode  # save on IO calls

    def export(self):
        '''Export the pin'''

        try:
            with open('/sys/class/gpio/export', 'w') as f:
                f.write(str(self._pin))
            with open('/sys/class/gpio/export', 'w') as f:
                f.write(str(self._pin))
        except PermissionError:
            pass  # will always fail the first time

    def unexport(self):
        '''Unexport the pin'''

        try:
            with open('/sys/class/gpio/unexport', 'w') as f:
                f.write(str(self._pin))
        except PermissionError:
            pass  # will always fail the first time

        with open('/sys/class/gpio/unexport', 'w') as f:
            f.write(str(self._pin))

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
            raise GpioError(f'Cannot set GPIO {self._pin.name} value, it is in input mode')

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

        return self._pin

    @property
    def pin(self) -> GpioPin:
        '''str: The pin name. Readonly.'''

        if self._pin == 0:
            return 'MOCKED'
        return GpioPin(self._pin)

    @property
    def name(self) -> str:
        '''str: The GPIO name. Readonly.'''

        return self._name
