from threading import Thread, Event

from .. import logger


class TimerLoop:
    '''Call a function in a loop after a delay.'''

    def __init__(self, name: str, loop_func, delay: float, exc_func=None):
        '''
        Parameters
        ----------
        name: str
            name to use when logging.
        loop_func
            The function to call in a loop. Function must return True to be called again.
        delay: float
            The delay between calls in seconds.
        exc_func
            Optional function to call if the loop raises an exception. Exception will be pass to
            the function as a argument.
        '''

        if not isinstance(delay, (int, float)):
            raise ValueError(f'{delay} is not a float')

        self._name = name
        self._thread = Thread(target=self._loop)
        self._event = Event()
        self._delay = delay
        self._loop_func = loop_func
        self._exc_func = exc_func
        self._looping = False

    def __del__(self):

        self.stop()

    def start(self):
        '''Start the timer'''

        logger.debug(f'starting {self._name} timer loop')

        self._thread.start()

        if self._event.is_set():
            self._event = Event()

    def _loop(self):

        self._looping = True

        ret = True
        while ret is True and not self._event.is_set():
            try:
                self._loop_func()
            except Exception as exc:
                self._event.set()
                logger.error(f'{self._name} timer loop loop_func raise: {exc}')
                if self._exc_func:
                    try:
                        self._exc_func(exc)
                    except Exception:
                        logger.error(f'{self._name} timer loop exc_func raise: {exc}')
                    break

            ret = self._event.wait(self._delay)

        self._looping = False

    def stop(self):
        '''Stop the timer'''

        logger.debug(f'stopping {self._name} timer loop')

        if not self._event.is_set():
            self._event.set()

        if self._thread.is_alive():
            self._thread.join()

    @property
    def delay(self) -> float:
        '''float: The delay between loops'''

        return self._delay

    @delay.setter
    def delay(self, value: float):

        if not isinstance(value, float):
            raise ValueError(f'{value} is not a float')

        self._delay = value

    @property
    def is_running(self) -> bool:
        '''bool: Status of the timer loop.'''

        return self._looping
