"""CAN network"""

from __future__ import annotations

import os
import subprocess
from enum import IntEnum, auto
from typing import Callable

import can
import canopen
import psutil
from loguru import logger


class CanNetworkError(Exception):
    """Error with the CANopen network / bus"""


NetworkError = CanNetworkError  # for backward compatibility


class CanNetworkState(IntEnum):
    """CAN network states."""

    NETWORK_NO_BUS = auto()
    NETWORK_INIT = auto()
    NETWORK_DOWN = auto()
    NETWORK_UP = auto()


class CanNetwork:
    """Abstract the CAN bus. Can handle downed or missing CAN bus."""

    def __init__(
        self,
        bus_type: str,
        channel: str,
        socketcand_host: str = "localhost",
        socketcand_port: int = 29536,
    ) -> None:
        self._bus_type = bus_type
        self._channel = channel
        self._socketcand_host = socketcand_host
        self._socketcand_port = socketcand_port

        self._reset_cbs: list[Callable[[], None]] = []
        self._nodes: list[canopen.Node] = []
        self._subscriptions: list[tuple[int, Callable[[int, bytes, float], None]]] = []
        self._bus: can.BusABC | None = None
        self._network: canopen.Network | None = None
        self._notifier: can.Notifier | None = None

        self._state = CanNetworkState.NETWORK_INIT

        if os.geteuid() != 0:  # running as root
            logger.warning("not running as root, cannot restart CAN bus if it goes down")

        self._first_no_bus = True  # flag to only log error message on _first error
        self._first_bus_down = True  # flag to only log error message on _first error

    def __del__(self) -> None:
        self._del()

    def _init(self) -> None:
        logger.info("(re)starting CAN network")
        try:
            self._bus = can.interface.Bus(
                interface=self._bus_type,
                host=self._socketcand_host,
                port=self._socketcand_port,
                channel=self._channel,
            )
        except Exception as e:  # pylint: disable=W0718
            logger.info(str(e))
            return

        self._network = canopen.Network(self._bus)
        self._notifier = can.Notifier(self._bus, self._network.listeners, 1)
        self._network.notifier = self._notifier
        try:
            for sub in self._subscriptions:
                self._network.subscribe(sub[0], sub[1])
            for reset_cb in self._reset_cbs:
                reset_cb()
        except Exception as e:  # pylint: disable=W0718
            logger.exception(e)

    def _del(self) -> None:
        if self._network is not None:
            try:
                self._network.disconnect()
            except Exception as e:  # pylint: disable=W0718
                logger.info(f"Error when disconnecting: {e}")
            del self._network
            self._network = None

        if self._notifier is not None:
            self._notifier.stop()
            del self._notifier
            self._notifier = None

        if self._bus is not None:
            self._bus.shutdown()
            del self._bus
            self._bus = None

    def _restart_bus(self) -> None:
        """Try to restart the CAN bus"""

        if self._bus:
            self._bus.shutdown()
            self._bus = None

        if os.geteuid() == 0:  # running as root
            cmd = (
                f"ip link set {self._channel} down;"
                f"ip link set {self._channel} type can bitrate 1000000;"
                f"ip link set {self._channel} up"
            )
            out = subprocess.run(cmd, shell=True, check=False)
            if out.returncode != 0:
                logger.error(out)

    def monitor(self) -> None:
        """Monitor the CAN bus/network"""

        if self._bus_type == "socketcand":
            if self._state != CanNetworkState.NETWORK_UP:
                self._init()
                self._state = CanNetworkState.NETWORK_UP
            return

        bus = psutil.net_if_stats().get(self._channel)

        if self._state == CanNetworkState.NETWORK_INIT:
            self._init()
            self._state = CanNetworkState.NETWORK_UP
        elif self._state == CanNetworkState.NETWORK_NO_BUS:
            if self._first_no_bus:
                logger.critical(f"{self._channel} does not exists, nothing OLAF can do")
                self._first_no_bus = False
            if bus is None:
                self._state = CanNetworkState.NETWORK_DOWN
        elif self._state == CanNetworkState.NETWORK_DOWN:
            if self._first_bus_down:
                logger.error(f"{self._channel} is down")
                self._first_bus_down = False
            if bus is None:
                self._first_no_bus = True  # reset flag
                self._del()
                self._state = CanNetworkState.NETWORK_NO_BUS
            elif not bus.isup:
                self._del()
                self._restart_bus()
            else:
                self._init()
                self._state = CanNetworkState.NETWORK_UP
        elif self._state == CanNetworkState.NETWORK_UP:
            if bus is None:
                self._first_no_bus = True  # reset flag
                self._del()
                self._state = CanNetworkState.NETWORK_NO_BUS
            elif not bus.isup:
                self._first_bus_down = True  # reset flag
                self._del()
                self._state = CanNetworkState.NETWORK_DOWN

    def add_reset_callback(self, reset_cb: Callable[[], None]) -> None:
        """Add CAN bus/network reset callback."""
        if self._network is not None:
            reset_cb()
        self._reset_cbs.append(reset_cb)

    @property
    def status(self) -> CanNetworkState:
        """CanState: CAN bus state."""
        return self._state

    def send_message(self, cob_id: int, data: bytes, raise_error: bool = True) -> None:
        """Send a CAN message."""
        if self._bus is None:
            if raise_error:
                raise CanNetworkError("can network is down")
            return
        try:
            self._bus.send(can.Message(arbitration_id=cob_id, data=data, is_extended_id=False))
        except Exception as e:  # pylint: disable=W0718
            if raise_error:
                raise CanNetworkError(str(e)) from e

    def subscribe(self, cob_id: int, callback: Callable[[int, bytes, float], None]) -> None:
        """Subscribe to CAN messages by the cob_id."""
        if self._network is not None:
            self._network.subscribe(cob_id, callback)
        self._subscriptions.append((cob_id, callback))

    def add_node(self, node: canopen.LocalNode | canopen.RemoteNode) -> None:
        """Add a node to the network."""
        if self._network is not None:
            self._network.add_node(node)

    @property
    def channel(self) -> str:
        """str: The CAN channel."""
        return self._channel
