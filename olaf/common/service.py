"""The OLAF base Service class. A Resource with a dedicated thread."""

from enum import IntEnum
from threading import Event, Thread

from loguru import logger

from ..canopen.node import Node


class ServiceState(IntEnum):
    """State a service can be in."""

    STOPPED = 0
    """Service is not running."""
    STARTING = 1
    """Service is starting up."""
    RUNNING = 2
    """Service is running."""
    STOPPING = 3
    """Service is stopping."""
    FAILED = 3
    """Service has failed."""


class Service:
    """
    OLAF service, basically a :py:class:`Resource` with a dedicated thread.

    All the ``on_*`` members can be overridden as needed.
    """

    def __init__(self):
        self.node = None
        """Node or MasterNode: The app's CANopen node. Set to None until start() is called."""

        self._event = Event()
        self._thread = Thread(target=self._loop)
        self._status = ServiceState.STOPPED
        self._error = False

    def __del__(self):
        if not self._event.is_set():
            self._event.set()

        if self._thread.is_alive():
            self._thread.join()

    def start(self, node: Node):
        """
        App will call this to start the service. This will call `self.on_start()` start a thread
        that will call `self.on_loop()`.
        """

        self._status = ServiceState.STARTING
        logger.debug(f"starting service {self.__class__.__name__}")
        self.node = node

        try:
            self.on_start()
            self._thread.start()
        except Exception as e:  # pylint: disable=W0718
            logger.exception(f"{self.__class__.__name__}'s on_start raised: {e}")
            logger.critical(f"{self.__class__.__name__}'s thread is being skipped")
            self._status = ServiceState.FAILED

    def on_start(self):
        """
        Called when the service starts.

        Should be used to add SDO read/write callbacks to app.
        """

        pass

    def _loop(self):
        """
        Loop until a exception is thrown or the app stops.
        """

        self._status = ServiceState.RUNNING

        while not self._event.is_set():
            try:
                self.on_loop()
            except Exception as e:  # pylint: disable=W0718
                logger.error("unexpected exception raised by on_loop, stopping service")
                self.on_loop_error(e)
                self._event.set()
                self._error = True

        self._status = ServiceState.STOPPING

    def on_loop(self):
        """
        Called when in a while loop.
        """

        self.sleep(1)

    def on_loop_error(self, error: Exception):
        """
        Called when on_loop raises an exception before the thread stops.

        Should be used to stop any hardware the service controls (if possible) and logs the errors.
        """

        logger.exception(f"{self.__class__.__name__} on_loop raised: {error}")

    def stop(self):
        """
        App will call this to stop the service when the app stops. This will call `self.on_stop()`.
        """

        self._status = ServiceState.STOPPING
        logger.debug(f"stopping service {self.__class__.__name__}")

        try:
            self.on_stop_before()
        except Exception as e:  # pylint: disable=W0718
            logger.exception(f"{self.__class__.__name__}'s on_stop_before raised: {e}")
            self._error = True

        if not self._event.is_set():
            self._event.set()

        if self._thread.is_alive():
            self._thread.join()

        try:
            self.on_stop()
        except Exception as e:  # pylint: disable=W0718
            logger.exception(f"{self.__class__.__name__}'s on_stop raised: {e}")
            self._error = True

        self._status = ServiceState.FAILED if self._error else ServiceState.STOPPED

    def on_stop_before(self):
        """
        Called when the app stops before the thread is stopped. Should be used to stop any blocking
        calls in the thread loop.

        Will be called reguardless if `self.on_loop_error()` was called or not when the app stops.
        """

        pass

    def on_stop(self):
        """
        Called when the app stops after the thread has stopped. Should be used to stop any hardware
        the service controls.

        Will be called reguardless if `self.on_loop_error()` was called or not when the app stops.
        """

        pass

    def sleep(self, timeout: float):
        """
        Sleep for X seconds, that can be interupted if `stop()` is called.

        Parameters
        ----------
        timeout: float
            The time to sleep in seconds.
        """

        self._event.wait(timeout)

    def sleep_ms(self, timeout: float):
        """
        Sleep for X milliseconds, that can be interupted if `stop()` is called.

        Parameters
        ----------
        timeout: float
            The time to sleep in milliseconds.
        """

        self._event.wait(timeout / 1000)

    def cancel(self):
        """Cancel the service. Can be used to stop the service from `self.on_loop()`."""

        self._event.set()

    @property
    def status(self) -> ServiceState:
        """ServiceState: Get the service state."""

        return self._status
