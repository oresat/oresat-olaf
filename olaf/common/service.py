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
        that will call on_loop.
        '''

        logger.debug(f'starting service {self.__class__.__name__}')
        self.node = node

        try:
            self.on_start()
        except Exception as e:
            logger.exception(f'{self.__class__.__name__}\'s on_start raised: {e}')

        self._thread.start()

    def on_start(self) -> None:
        '''
        Called when the service starts.
        '''

        pass

    def _loop(self):

        while not self._event.is_set():
            try:
                self.on_loop()
            except Exception as e:
                self.on_loop_error(e)

    def on_loop(self):
        '''
        Called when in a while loop.
        '''

        self.sleep(1)

    def on_loop_error(self, error: Exception):
        '''
        Called when on_loop raises an exception.
        '''

        logger.exception(f'{self.__class__.__name__} on_loop raised: {error}')

    def stop(self):
        '''
        App will call this to stop the service. This will call `self.on_stop()`.
        '''

        logger.debug(f'stopping service {self.__class__.__name__}')

        if not self._event.is_set():
            self._event.set()

        if self._thread.is_alive():
            self._thread.join()

        try:
            self.on_stop()
        except Exception as e:
            logger.exception(f'{self.__class__.__name__}\'s on_stop raised: {e}')

    def on_stop(self) -> None:
        '''
        Called when the program stops and if the services fails. Should be used to stop any
        hardware the service controls.
        '''

        pass

    def sleep(self, timeout: float):
        '''
        Sleep for time, that can be interupted if `stop()` is called.

        Parameters
        ----------
        timeout: float
            The time to sleep in seconds.
        '''

        self._event.wait(timeout)
