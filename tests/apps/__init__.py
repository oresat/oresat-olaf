from threading import Thread, Event
from loguru import logger

import canopen
from oresat_linux_node import OreSatNode, App


class TestNode(Thread):
    def __init__(self):
        super().__init__()
        logger.disable('oresat_linux_node')
        self.node = canopen.LocalNode(0x10, 'oresat_linux_node.eds')

    def add_app(self, app: App):
        self.app = app
        self.node.add_read_callback(self.app.on_read)
        self.node.add_write_callback(self.app.on_write)

    def run(self):
        self.event = Event()
        self.app.start()
        self.app.run(self.event)
        self.app.end()

    def stop(self):
        self.event.set()
        self.join()
