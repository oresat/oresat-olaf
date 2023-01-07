from threading import Thread, Event

from .. import logger


class TimerLoop:
    '''Call a function in a loop after a delay.'''

    def __init__(self, name: str, loop_func, delay: float, start_delay=0.0, args=(),
                 exc_func=None):
        '''
        Parameters
        ----------
        name: str
            name to use when logging.
        loop_func
            The function to call in a loop. Function must return True to be called again.
        delay: int, float
            The delay between calls in seconds.
        start_delay: int,float
            Optional delay in seconds before the loop_func is called the first time.
        args: tuple
            Optional arguments to pass to loop_func
        exc_func
            Optional function to call if the loop raises an exception. Exception will be pass to
            the function as a argument.
        '''

        if not isinstance(delay, (int, float)):
            raise ValueError(f'delay of {delay} is not a int or float')

        if not isinstance(start_delay, (int, float)):
            raise ValueError(f'start_delay of {start_delay} is not a int or float')

        self._name = name
        self._loop_func = loop_func
        self._delay = float(delay)
        self._start_delay = float(start_delay)
        self._args = args
        self._exc_func = exc_func
        self._thread = Thread(name=name, target=self._loop)
        self._event = Event()

    def __del__(self):

        self.stop()

    def start(self):
        '''Start the timer'''

        logger.debug(f'starting {self._name} timer loop')

        if self._event.is_set():
            self._event = Event()

        self._thread.start()

    def _loop(self):

        if self._start_delay > 0:
            self._event.wait(self._start_delay)

        ret = True
        while ret is True and not self._event.is_set():
            try:
                ret = self._loop_func(*self._args)
            except Exception as exc:
                self._event.set()
                logger.error(f'{self._name} timer loop loop_func raise: {exc}')
                if self._exc_func:
                    try:
                        self._exc_func(exc)
                    except Exception:
                        logger.error(f'{self._name} timer loop exc_func raise: {exc}')

            self._event.wait(self._delay)

    def stop(self):
        '''Stop the timer'''

        if not self._event.is_set():
            logger.debug(f'stopping {self._name} timer loop')
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

        return self._thread.is_alive()

    @property
    def name(self) -> str:
        '''str: The name of the TimerLoop.'''

        return self._name
