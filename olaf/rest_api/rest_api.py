from threading import Thread

from flask import Flask
from werkzeug.serving import make_server
from loguru import logger


class RestAPI:

    def __init__(self, name, node):
        self.node = node
        self.app = Flask(name)
        self.server = make_server('localhost', 5000, self.app)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.thread = Thread(target=self._run)

    def start(self):
        logger.info('starting rest api')
        self.thread.start()

    def _run(self):
        self.server.serve_forever()

    def stop(self):
        logger.info('stopping rest api')
        self.server.shutdown()

    def add_blueprint(self, blueprint):
        self.app.register_blueprint(blueprint)
