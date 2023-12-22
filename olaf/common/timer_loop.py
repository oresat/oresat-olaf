"""A quick timer-based class that calls a function in a loop"""

from threading import Event, Thread
from time import monotonic
from typing import Union

import canopen

from .. import logger


class TimerLoop:
    """Call a function in a loop after a delay."""

    def __init__(
        self,
        name: str,
        loop_func,
        delay: Union[int, float, canopen.objectdictionary.Variable],
        start_delay: Union[int, float, canopen.objectdictionary.Variable] = 0,
        args: tuple = (),
        exc_func=None,
    ):
        """
        Parameters
        ----------
        name: str
            Nice name to use when logging.
        loop_func
            The function to call in a loop. Function must return True to be called again.
        delay: int, float, Variable
            The delay between calls in milliseconds. Can be a Variable to allow the value to be
            changed with a SDO.
        start_delay: int, float, Variable
            Optional delay in milliseconds before the loop_func is called the first time. Can be a
            Variable to allow the value to be changed with a SDO. Defaults to 0.
        args: tuple
            Optional arguments to pass to loop_func.
        exc_func
            Optional function to call if the loop raises an exception. Exception will be pass to
            the function as a argument.
        """

        if not isinstance(delay, (int, float, canopen.objectdictionary.Variable)):
            raise ValueError(f"delay of {delay} is not a int, float, Variable")

        if not isinstance(start_delay, (int, float, canopen.objectdictionary.Variable)):
            raise ValueError(f"start_delay of {start_delay} is not a int, float, or Variable")

        self._name = name
        self._loop_func = loop_func
        self._delay = delay
        self._start_delay = start_delay
        self._args = args
        self._exc_func = exc_func
        self._thread = Thread(name=name, target=self._loop)
        self._event = Event()
        self._start_time = monotonic()

    def __del__(self):
        self.stop()

    def start(self):
        """Start the timer"""

        logger.debug(f"starting {self._name} timer loop")

        if self._event.is_set():
            self._event = Event()

        self._start_time = monotonic()
        self._thread.start()

    def _loop(self):
        is_var = isinstance(self._start_delay, canopen.objectdictionary.Variable)
        if is_var and self._start_delay.value > 0:
            self._event.wait(self._start_delay.value / 1000)
            self._start_time = monotonic()
        elif not is_var and self._start_delay > 0:
            self._event.wait(self._start_delay / 1000)
            self._start_time = monotonic()

        ret = True
        while ret is True and not self._event.is_set():
            try:
                ret = self._loop_func(*self._args)
            except Exception as e:  # pylint: disable=W0718
                self._event.set()
                logger.exception(f"{self._name} timer loop loop_func raise: {e}")
                if self._exc_func:
                    try:
                        self._exc_func(e)
                    except Exception as e2:  # pylint: disable=W0718
                        logger.exception(f"{self._name} timer loop exc_func raise: {e2}")

            if isinstance(self._delay, canopen.objectdictionary.Variable):
                delay = self._delay.value / 1000
            else:
                delay = self._delay / 1000
            self._event.wait(delay - ((monotonic() - self._start_time) % delay))

    def stop(self):
        """Stop the timer"""

        if not self._event.is_set():
            logger.debug(f"stopping {self._name} timer loop")
            self._event.set()

        if self._thread.is_alive():
            self._thread.join()

    @property
    def delay(self) -> [int, float, canopen.objectdictionary.Variable]:
        """int, float, Variable: The delay between loops"""

        return self._delay

    @delay.setter
    def delay(self, value: Union[int, float, canopen.objectdictionary.Variable]):
        if not isinstance(value, (int, float, canopen.objectdictionary.Variable)):
            raise ValueError(f"{value} is not a int, float, or Variable")

        self._start_time = monotonic()
        self._delay = value

    @property
    def is_running(self) -> bool:
        """bool: Status of the timer loop."""

        return self._thread.is_alive()

    @property
    def name(self) -> str:
        """str: The name of the TimerLoop."""

        return self._name
