"""Unit tests for generic Service operation"""

import unittest
from threading import Event

from olaf import Service, ServiceState


class ServiceTesterException(Exception):
    """Named custom exception, indicates that it was intentional for a test"""

    pass


class ServiceTester(Service):
    """Base class for checking that Service is functioning as intended

    Unit tests can derive from this class to override a method with new test behavior.
    """

    def __init__(self, test):
        super().__init__()
        self.test = test
        self.did_on_start = Event()
        self.did_on_loop = Event()
        self.did_on_loop_error = Event()
        self.did_on_stop_before = Event()
        self.did_on_stop = Event()

    def on_start(self):
        self.did_on_start.set()
        self.test.assertEqual(self.status, ServiceState.STARTING, self.__class__.__name__)

    def on_loop(self):
        self.did_on_loop.set()
        # on_loop() can run during a stop(), so in states RUNNING and STOPPING. It may be run
        # while on_stop_before() is being run, but by the time on_stop() is called there should
        # be no more iterations.
        self.test.assertFalse(self.did_on_stop.is_set(), self.__class__.__name__)
        self.test.assertIn(
            self.status, (ServiceState.RUNNING, ServiceState.STOPPING), self.__class__.__name__
        )

    def on_loop_error(self, error: Exception):
        self.did_on_loop_error.set()
        self.test.assertTrue(self.did_on_loop.is_set(), self.__class__.__name__)
        self.test.assertEqual(self.status, ServiceState.RUNNING, self.__class__.__name__)
        self.test.assertIsInstance(error, ServiceTesterException, self.__class__.__name__)

    def on_stop_before(self):
        self.did_on_stop_before.set()
        self.test.assertEqual(self.status, ServiceState.STOPPING, self.__class__.__name__)
        self.test.assertFalse(self.did_on_stop.is_set(), self.__class__.__name__)

    def on_stop(self):
        self.did_on_stop.set()
        self.test.assertEqual(self.status, ServiceState.STOPPING, self.__class__.__name__)
        self.test.assertTrue(self.did_on_stop_before.is_set(), self.__class__.__name__)

    def raise_exception(self):
        """Helper method for raising the test exception in lambdas"""
        raise ServiceTesterException(self.__class__.__name__)


class TestService(unittest.TestCase):
    """Tests the Service state machine"""

    def test_normal_operation(self):
        """Tests the normal Service lifecycle - creation -> start -> stop"""

        service = ServiceTester(self)
        self.assertEqual(service.status, ServiceState.STOPPED)

        service.start(node=None)
        self.assertIn(service.status, (ServiceState.STARTING, ServiceState.RUNNING))
        self.assertTrue(service.did_on_start.is_set())

        self.assertTrue(service.did_on_loop.wait(timeout=0.1))

        service.stop()
        self.assertEqual(service.status, ServiceState.STOPPED)
        self.assertTrue(service.did_on_stop_before.is_set())
        self.assertTrue(service.did_on_stop.is_set())

    def test_cancel_operation(self):
        """Tests that cancel() works in the on_loop() callback"""
        # fmt: off
        ServiceCancel = type("ServiceCancel", (ServiceTester,), {
            "on_loop": lambda self: (self.did_on_loop.set(), self.cancel())
        })  # fmt: on
        service = ServiceCancel(self)
        service.start(node=None)
        self.assertTrue(service.did_on_loop.wait(timeout=0.1))
        self.assertEqual(service.status, ServiceState.STOPPING)

    def test_sleep(self):
        """Tests that sleep() works in on_loop(), and that stop() can interrupt it"""
        # fmt: off
        ServiceSleep = type("ServiceSleep", (ServiceTester,), {
            "on_loop": lambda self: (self.did_on_loop.set(), self.sleep(None))
        })  # fmt: on
        service = ServiceSleep(self)
        service.start(node=None)
        self.assertTrue(service.did_on_loop.wait(timeout=0.1))
        self.assertEqual(service.status, ServiceState.RUNNING)

        service.stop()
        self.assertEqual(service.status, ServiceState.STOPPED)

    def test_on_start_failed(self):
        """Tests what happens when an exception is raised in on_start()"""
        # fmt: off
        BadStart = type("BadStart", (ServiceTester,), {
            "on_start": lambda self: self.raise_exception()
        })  # fmt: on
        service = BadStart(self)
        service.start(node=None)
        self.assertEqual(service.status, ServiceState.FAILED)

    def test_on_loop_failed(self):
        """Tests what happens when an exception is raised in on_loop()"""
        # fmt: off
        BadLoop = type("BadLoop", (ServiceTester,), {
            "on_loop": lambda self: (self.did_on_loop.set(), self.raise_exception())
        })  # fmt: on
        service = BadLoop(self)
        service.start(node=None)
        self.assertTrue(service.did_on_loop.wait(timeout=0.1))
        self.assertTrue(service.did_on_loop_error.is_set())
        self.assertEqual(service.status, ServiceState.STOPPING)

    @unittest.skip("FIXME: What should happen here? Currently crashes but leaves state RUNNING")
    def test_on_loop_error_failed(self):
        """Tests when an exception is raised while handling an exception from on_loop()"""
        # fmt: off
        BadLoopError = type("BadLoopError", (ServiceTester,), {
            "on_loop": lambda self: (self.did_on_loop.set(), self.raise_exception()),
            "on_loop_error": lambda self, e: (self.did_on_loop_error.set(), self.raise_exception())
        })  # fmt: on
        service = BadLoopError(self)
        service.start(node=None)
        self.assertTrue(service.did_on_loop.wait(timeout=0.1))
        self.assertTrue(service.did_on_loop_error.is_set())
        self.assertEqual(service.status, ServiceState.RUNNING)

    def test_on_stop_before_failed(self):
        """Tests what happens when an exception is raised in on_stop_before()"""
        # fmt: off
        BadStopBefore = type("BadStopBefore", (ServiceTester,), {
            "on_stop_before": lambda self: self.raise_exception()
        })  # fmt: on
        service = BadStopBefore(self)
        service.start(node=None)
        service.stop()
        self.assertEqual(service.status, ServiceState.FAILED)

    def test_on_stop_failed(self):
        """Tests what happens when an exception is raised in on_stop()"""
        # fmt: off
        BadStop = type("BadStop", (ServiceTester,), {
            "on_stop": lambda self: self.raise_exception()
        })  # fmt: on
        service = BadStop(self)
        service.start(node=None)
        service.stop()
        self.assertEqual(service.status, ServiceState.FAILED)
