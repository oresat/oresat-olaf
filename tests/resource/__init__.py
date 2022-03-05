from threading import Thread, Event
from loguru import logger

import canopen
from olaf import Resource


class TestApp(Thread):
    def __init__(self):
        super().__init__()
        logger.disable('oresat_app')
        self.node = canopen.LocalNode(0x10, 'oresat_app.eds')

    def add_resource(self, resource: Resource):
        self.resource = resource
        self.node.add_read_callback(self.resource.on_read)
        self.node.add_write_callback(self.resource.on_write)

    def run(self):
        self.event = Event()
        self.resource.on_start()
        while not self.event.is_set():
            self.resource.on_loop()
            self.event.wait(self.resource.delay)
        self.resource.on_end()

    def stop(self):
        self.event.set()
        self.join()
