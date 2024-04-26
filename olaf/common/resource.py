"""The OreSat Linux base app resource. It is a nice way to organize OD callbacks."""

from loguru import logger

from ..canopen.node import Node


class Resource:
    """
    OreSat Linux app resource. Used to setup OD callbacks in a common, isolated environment.

    All the ``on_*`` members can be overridden as needed.
    """

    def __init__(self):
        self.node = None
        """Node or MasterNode: The app's CANopen node. Set to None until start() is called."""

    def start(self, node: Node):
        """
        App will call this to start the resource. This will call `self.on_start()`.
        """

        logger.debug(f"starting resource {self.__class__.__name__}")
        self.node = node

        try:
            self.on_start()
        except Exception as e:  # pylint: disable=W0718
            logger.exception(
                f"{self.__class__.__name__}'s on_start raised an uncaught exception:" f"{e}"
            )

    def end(self):
        """
        App will call this to stop the resource. This will call `self.on_end()`.
        """

        logger.debug(f"stopping resource {self.__class__.__name__}")

        try:
            self.on_end()
        except Exception as e:  # pylint: disable=W0718
            logger.exception(
                f"{self.__class__.__name__}'s on_end raised an uncaught exception:" f"{e}"
            )

    def on_start(self) -> None:
        """
        Start the resource.
        """

        pass

    def on_end(self) -> None:
        """Called when the program ends and if the resources fails. Should be used to stop hardware
        and can be used to zero/clear resource's data in object dictionary as needed."""

        pass
