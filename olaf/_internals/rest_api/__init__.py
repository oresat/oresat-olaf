import os
from threading import Thread

from flask import Flask, Blueprint, render_template, send_from_directory
from werkzeug.serving import make_server
from loguru import logger

from .blueprints import core_templates_bp


class RestAPI:
    '''
    An optional Flask app for reading and writing values into the OD.

    Use the global ``olaf.rest_api`` object.
    '''

    def __init__(self):
        self._app = Flask(os.uname()[1])
        self._thread = Thread(target=self._run)
        self._server = None
        self._ctx = None

        # add core blueprint
        self._app.register_blueprint(core_templates_bp)

    def start(self, address: str, port: int):
        '''Start the REST API thread'''
        logger.info('starting rest api')
        self._server = make_server(address, port, self._app)
        self._ctx = self._app.app_context()
        self._ctx.push()
        self._thread.start()

    def _run(self):
        self._server.serve_forever()

    def stop(self):
        '''Stop the REST API thread'''
        logger.info('stopping rest api')
        if self._server is not None:
            self._server.shutdown()
        if self._thread.is_alive():
            self._thread.join()

    def add_blueprint(self, blueprint: Blueprint):
        '''Add a :py:class:`Blueprint` to the internal Flask app.

        Parameters
        ----------
        blueprint: Blueprint
            The blueprint to add to the Flask app
        '''

        self._app.register_blueprint(blueprint)


rest_api = RestAPI()
'''The global instance of the REST API.'''


@rest_api._app.route('/')
def root():

    routes = []
    for p in rest_api._app.url_map.iter_rules():
        route = str(p)
        if not route.startswith('/static/') and not route.startswith('/od/') \
                and route not in ['/', '/favicon.ico']:
            routes.append(str(p))

    title = os.uname()[1]
    routes = sorted(routes)

    return render_template('root.html', title=title, routes=routes)


@rest_api._app.route('/favicon.ico')
def favicon():
    path = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(f'{path}/static', 'favicon.ico')
