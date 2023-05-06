from threading import Thread, Event

from canopen.objectdictionary import Variable

from .. import logger


class TimerLoop:
    '''Call a function in a loop after a delay.'''

    def __init__(self, name: str, loop_func, delay: [int, float, Variable],
                 start_delay: [int, float, Variable] = 0, args: tuple = (), exc_func=None):
        '''
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
        '''

        if not isinstance(delay, (int, float, Variable)):
            raise ValueError(f'delay of {delay} is not a int, float, Variable')

        if not isinstance(start_delay, (int, float, Variable)):
            raise ValueError(f'start_delay of {start_delay} is not a int, float, or Variable')

        self._name = name
        self._loop_func = loop_func
        self._delay = delay
        self._start_delay = start_delay
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

        if isinstance(self._start_delay, Variable) and self._start_delay.value > 0:
            self._event.wait(self._start_delay.value / 1000)
        elif not isinstance(self._start_delay, Variable) and self._start_delay > 0:
            self._event.wait(self._start_delay / 1000)

        ret = True
        while ret is True and not self._event.is_set():
            try:
                ret = self._loop_func(*self._args)
            except Exception as e:
                self._event.set()
                logger.exception(f'{self._name} timer loop loop_func raise: {e}')
                if self._exc_func:
                    try:
                        self._exc_func(e)
                    except Exception as e:
                        logger.exception(f'{self._name} timer loop exc_func raise: {e}')

            if isinstance(self._delay, Variable):
                self._event.wait(self._delay.value / 1000)
            else:
                self._event.wait(self._delay / 1000)

    def stop(self):
        '''Stop the timer'''

        if not self._event.is_set():
            logger.debug(f'stopping {self._name} timer loop')
            self._event.set()

        if self._thread.is_alive():
            self._thread.join()

    @property
    def delay(self) -> [int, float, Variable]:
        '''int, float, Variable: The delay between loops'''

        return self._delay

    @delay.setter
    def delay(self, value: [int, float, Variable]):

        if not isinstance(value, int) or not isinstance(value, float) \
                or not isinstance(value, Variable):
            raise ValueError(f'{value} is not a int, float, or Variable')

        self._delay = value

    @property
    def is_running(self) -> bool:
        '''bool: Status of the timer loop.'''

        return self._thread.is_alive()

    @property
    def name(self) -> str:
        '''str: The name of the TimerLoop.'''

        return self._name
