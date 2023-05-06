import os
import base64
import shutil
import logging
from enum import IntEnum
from pathlib import Path
from threading import Thread

import canopen
from flask import Flask, render_template, jsonify, request, send_from_directory
from loguru import logger
from natsort import natsorted
from werkzeug.serving import make_server

from ..app import app

_TITLE = os.uname()[1]
_PATH = os.path.dirname(os.path.abspath(__file__))
_TEMPLATE_DIR = '/tmp/oresat/templates'


class DataType(IntEnum):
    BOOLEAN = 0x1
    INTEGER8 = 0x2
    INTEGER16 = 0x3
    INTEGER32 = 0x4
    UNSIGNED8 = 0x5
    UNSIGNED16 = 0x6
    UNSIGNED32 = 0x7
    REAL32 = 0x8
    VISIBLE_STRING = 0x9
    OCTET_STRING = 0xA
    UNICODE_STRING = 0xB
    DOMAIN = 0xF
    REAL64 = 0x11
    INTEGER64 = 0x15
    UNSIGNED64 = 0x1B


INT_TYPES = [
    DataType.INTEGER8,
    DataType.INTEGER16,
    DataType.INTEGER32,
    DataType.INTEGER64,
    DataType.UNSIGNED8,
    DataType.UNSIGNED16,
    DataType.UNSIGNED32,
    DataType.UNSIGNED64
]


class RestAPI:
    '''
    An optional Flask app for reading and writing values into the OD.

    Use the global ``olaf.rest_api`` object.
    '''

    def __init__(self):

        self.app = Flask(_TITLE, template_folder=_TEMPLATE_DIR, static_folder=f'{_PATH}/static')
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        self._thread = Thread(target=self._run)
        self._server = None
        self._ctx = None
        Path(_TEMPLATE_DIR).mkdir(parents=True, exist_ok=True)

        # add all core templates
        for i in os.listdir(f'{_PATH}/templates'):
            self.add_template(f'{_PATH}/templates/{i}')

    def setup(self, address: str, port: int):
        '''Setup the REST API thread'''

        self._server = make_server(address, port, self.app)

    def start(self):
        '''Start the REST API thread'''

        logger.info('starting rest api')
        self._ctx = self.app.app_context()
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

    def add_template(self, template_path: str):
        '''
        Add a Flask template to common templates dir. All templates must be in the same directory.

        Parameters
        ----------
        template_path: str
            Path to the template file to add.
        '''

        shutil.copy(template_path, _TEMPLATE_DIR)


def render_olaf_template(template: str, name: str):
    '''
    Render a standard OLAF template.

    Parameters
    ----------
    template: str
        Template file name.
    name: str
        Nice name for the template.
    '''
    return render_template(template, title=_TITLE, name=name)


rest_api = RestAPI()
'''The global instance of the REST API.'''


@rest_api.app.route('/')
def root():

    routes = []
    for p in rest_api.app.url_map.iter_rules():
        route = str(p)
        if not route.startswith('/static/') and not route.startswith('/od/') \
                and route not in ['/', '/favicon.ico']:
            routes.append(str(p))

    routes = natsorted(routes)

    return render_template('root.html', title=os.uname()[1], routes=routes)


@rest_api.app.route('/favicon.ico')
def favicon():
    path = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(f'{path}/static', 'favicon.ico')


@rest_api.app.route('/od/<index>/', methods=['GET', 'PUT'])
def od_index(index: str):

    try:
        index = int(index, 16) if index.startswith('0x') else int(index)
    except ValueError:
        return jsonify({'error': f'invalid index {index}'})

    try:
        obj = app.node.od[index]
    except Exception:
        msg = f'no object at index {index:02X}'
        logger.error(f'RestApiError: {msg}')
        return jsonify({'error': msg})

    if request.method == 'PUT':
        raw = request.json['value']
        data_type = obj.data_type

        if data_type == DataType.DOMAIN:
            app.node._node.sdo[index].raw = base64.decodebytes(raw.encode('utf-8'))
        else:
            app.node._node.sdo[index].phys = raw_to_value(data_type, raw)

    return jsonify(object_to_json(index))


@rest_api.app.route('/od/<index>/<subindex>/', methods=['GET', 'PUT'])
def od_subindex(index: str, subindex: str):

    try:
        index = int(index, 16) if index.startswith('0x') else int(index)
        subindex = int(subindex, 16) if subindex.startswith('0x') else int(subindex)
    except ValueError:
        return jsonify({'error': f'invalid index {index} or subindex {subindex}'})

    try:
        obj = app.node.od[index][subindex]
    except Exception:
        msg = f'no object at index {index:04X} subindex {subindex:02X}'
        logger.error(f'RestApiError: {msg}')
        return jsonify({'error': msg})

    if request.method == 'PUT':
        raw = request.json['value']
        data_type = obj.data_type

        if data_type == DataType.DOMAIN:
            app.node._node.sdo[index][subindex].raw = base64.decodebytes(raw.encode('utf-8'))
        else:
            app.node._node.sdo[index][subindex].phys = raw_to_value(data_type, raw)

    return jsonify(object_to_json(index, subindex))


def raw_to_value(data_type: DataType, raw):
    value = None

    if data_type == DataType.BOOLEAN and not isinstance(raw, bool):
        value = True if raw.lower() == 'true' else False
    elif data_type in INT_TYPES and not isinstance(raw, int):
        value = int(raw, 16) if raw.startswith('0x') else int(raw)
    elif data_type in [DataType.REAL32, DataType.REAL64]:
        value = float(raw)
    else:
        value = raw

    return value


def object_to_json(index: int, subindex: int = None) -> dict:

    if subindex is None:
        try:
            obj = app.node.od[index]
            if isinstance(obj, canopen.objectdictionary.Variable):
                if obj.data_type == DataType.DOMAIN:
                    raw = app.node._node.sdo[index].raw
                    value = base64.encodebytes(raw).decode('utf-8')
                else:
                    value = app.node._node.sdo[index].phys
        except Exception as e:
            logger.debug(e)
            return {'error': f'0x{index:04X} is not a valid index'}
    else:
        try:
            obj = app.node.od[index][subindex]
            if obj.data_type == DataType.DOMAIN:
                raw = app.node._node.sdo[index][subindex].raw
                value = base64.encodebytes(raw).decode('utf-8')
            else:
                value = app.node._node.sdo[index][subindex].phys
        except Exception as e:
            logger.debug(e)
            return {'error': f'0x{subindex:02X} not a valid subindex for index 0x{index:04X}'}

    data = {
        'name': obj.name,
    }

    if isinstance(obj, canopen.objectdictionary.Variable):
        data['object_type'] = 'VARIABLE'
        data['access_type'] = obj.access_type
        data['data_type'] = DataType(obj.data_type).name
        if obj.access_type == 'wo':
            data['value'] = ''
        else:
            data['value'] = value
    elif isinstance(obj, canopen.objectdictionary.Array):
        data['object_type'] = 'ARRAY'
        data['subindexes'] = {subindex: object_to_json(index, subindex) for subindex in obj}
    else:
        data['object_type'] = 'RECORD'
        data['subindexes'] = {subindex: object_to_json(index, subindex) for subindex in obj}

    return data


@rest_api.app.route('/od')
def od_template():
    return render_olaf_template('od.html', name='Object Dictionary')


@rest_api.app.route('/os-command')
def os_command_template():
    return render_olaf_template('os_command.html', name='OS Command')


@rest_api.app.route('/system-info')
def system_info_template():
    return render_olaf_template('system_info.html', name='System Info')


@rest_api.app.route('/updater')
def updater_template():
    return render_olaf_template('updater.html', name='Updater')


@rest_api.app.route('/fwrite')
def fwrite_template():
    return render_olaf_template('fwrite.html', name='Fwrite')


@rest_api.app.route('/fread')
def fread_template():
    return render_olaf_template('fread.html', name='Fread')


@rest_api.app.route('/logs')
def logs_template():
    return render_olaf_template('logs.html', name='Logs')


@rest_api.app.route('/power-control')
def power_control_template():
    return render_olaf_template('power_control.html', name='Power Control')
