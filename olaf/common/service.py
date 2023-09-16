'''The OLAF base Service class. A Resource with a dedicated thread.'''

from threading import Thread, Event

from loguru import logger

from .._internals.node import Node


class Service:
    '''
    OLAF service, basically a :py:class:`Resource` with a dedicated thread.

    All the ``on_*`` members can be overridden as needed.
    '''

    def __init__(self):

        self.node = None
        self._event = Event()
        self._thread = Thread(target=self._loop)

    def __del__(self):

        if not self._event.is_set():
            self._event.set()

        if self._thread.is_alive():
            self._thread.join()

    def start(self, node: Node):
        '''
        App will call this to start the service. This will call `self.on_start()` start a thread
        that will call `self.on_loop()`.
        '''

        logger.debug(f'starting service {self.__class__.__name__}')
        self.node = node

        try:
            self.on_start()
            self._thread.start()
        except Exception as e:
            logger.exception(f'{self.__class__.__name__}\'s on_start raised: {e}')
            logger.critical(f'{self.__class__.__name__}\'s thread is being skipped')

    def on_start(self):
        '''
        Called when the service starts.

        Should be used to add SDO read/write callbacks to app.
        '''

        pass

    def _loop(self):
        '''
        Loop until a exception is thrown or the app stops.
        '''

        while not self._event.is_set():
            try:
                self.on_loop()
            except Exception as e:
                logger.error('unexpected exception raised by on_loop, stopping service')
                self.on_loop_error(e)
                self._event.set()

    def on_loop(self):
        '''
        Called when in a while loop.
        '''

        self.sleep(1)

    def on_loop_error(self, error: Exception):
        '''
        Called when on_loop raises an exception before the thread stops.

        Should be used to stop any hardware the service controls (if possible) and logs the errors.
        '''

        logger.exception(f'{self.__class__.__name__} on_loop raised: {error}')

    def stop(self):
        '''
        App will call this to stop the service when the app stops. This will call `self.on_stop()`.
        '''

        logger.debug(f'stopping service {self.__class__.__name__}')

        try:
            self.on_stop_before()
        except Exception as e:
            logger.exception(f'{self.__class__.__name__}\'s on_stop_before raised: {e}')

        if not self._event.is_set():
            self._event.set()

        if self._thread.is_alive():
            self._thread.join()

        try:
            self.on_stop()
        except Exception as e:
            logger.exception(f'{self.__class__.__name__}\'s on_stop raised: {e}')

    def on_stop_before(self):
        '''
        Called when the app stops before the thread is stopped. Should be used to stop any blocking
        calls in the thread loop.

        Will be called reguardless if `self.on_loop_error()` was called or not when the app stops.
        '''

        pass

    def on_stop(self):
        '''
        Called when the app stops after the thread has stopped. Should be used to stop any hardware
        the service controls.

        Will be called reguardless if `self.on_loop_error()` was called or not when the app stops.
        '''

        pass

    def sleep(self, timeout: float):
        '''
        Sleep for X seconds, that can be interupted if `stop()` is called.

        Parameters
        ----------
        timeout: float
            The time to sleep in seconds.
        '''

        self._event.wait(timeout)

    def sleep_ms(self, timeout: float):
        '''
        Sleep for X milliseconds, that can be interupted if `stop()` is called.

        Parameters
        ----------
        timeout: float
            The time to sleep in milliseconds.
        '''

        self._event.wait(timeout / 1000)
