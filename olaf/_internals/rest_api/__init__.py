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
    DataType.UNSIGNED64,
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


def make_error_json(error: str) -> str:
    '''
    Make the stand error json message for the REST API

    Parameters
    ----------
    error: str
        The error message

    Returns
    -------
    str
        The JSON error message
    '''

    return jsonify({'error': error})


rest_api = RestAPI()
'''The global instance of the REST API.'''


@rest_api.app.route('/')
def root():

    routes = []
    for p in rest_api.app.url_map.iter_rules():
        route = str(p)
        if not route.startswith('/static/') and not route.startswith('/od/') \
                and route not in ['/', '/favicon.ico', '/od-all']:
            routes.append(str(p))

    routes = natsorted(routes)

    return render_template('root.html', title=os.uname()[1], routes=routes)


@rest_api.app.route('/favicon.ico')
def favicon():
    path = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(f'{path}/static', 'favicon.ico')


def _json_value_to_value(data_type: DataType, json_value):
    '''Convert JSON value to real OD value to bytes for SDO callback'''

    if data_type == DataType.BOOLEAN and not isinstance(json_value, bool):
        value = True if json_value.lower() == 'true' else False
    elif data_type in INT_TYPES and not isinstance(json_value, int):
        value = int(json_value, 16) if json_value.startswith('0x') else int(json_value)
    elif data_type in [DataType.REAL32, DataType.REAL64]:
        value = float(json_value)
    elif data_type == DataType.DOMAIN:
        value = base64.decodebytes(json_value.encode('utf-8'))
    else:  # str
        value = json_value

    return value


@rest_api.app.route('/od/<index>/', methods=['GET', 'PUT'])
def od_index(index: str):

    try:
        index = int(index, 16) if index.startswith('0x') else int(index)
    except ValueError:
        return make_error_json(f'invalid index {index}')

    try:
        obj = app.od[index]
    except Exception:
        msg = f'no object at index {index:02X}'
        logger.error(f'REST API error: {msg}')
        return make_error_json(msg)

    if request.method == 'PUT':
        try:
            json_value = request.json['value']

            # convert value from JSON to bytes for SDO callback
            value = _json_value_to_value(obj.data_type, json_value)
            raw = obj.encode_raw(value)

            app.node._on_sdo_write(index, 0, obj, raw)
        except Exception as e:
            logger.error(f'REST API error: {e}')
            return make_error_json(str(e))

    return jsonify(_object_to_dict(index))


@rest_api.app.route('/od/<index>/<subindex>/', methods=['GET', 'PUT'])
def od_subindex(index: str, subindex: str):

    try:
        index = int(index, 16) if index.startswith('0x') else int(index)
        subindex = int(subindex, 16) if subindex.startswith('0x') else int(subindex)
    except ValueError:
        return make_error_json(f'invalid index {index} or subindex {subindex}')

    try:
        obj = app.od[index][subindex]
    except Exception:
        msg = f'no object at index {index:04X} subindex {subindex:02X}'
        logger.error(f'REST API error: {msg}')
        return make_error_json(msg)

    if request.method == 'PUT':
        try:
            json_value = request.json['value']

            # convert value from JSON to bytes for SDO callback
            value = _json_value_to_value(obj.data_type, json_value)
            raw = obj.encode_raw(value)

            app.node._on_sdo_write(index, subindex, obj, raw)
        except Exception as e:
            logger.error(f'REST API error: {e}')
            return make_error_json(str(e))

    return jsonify(_object_to_dict(index, subindex))


def _object_to_dict(index: int, subindex: int = None) -> dict:
    '''
    Convert a OD object to a dictionary.

    Parameters
    ----------
    index: int
        The index of the object to convert.
    subindex: int
        Optional subindex of the object to convert.

    Returns
    -------
    dict
        The object as a dictionary.
    '''

    if subindex is None:
        try:
            obj = app.node.od[index]
        except Exception:
            msg = f'0x{index:04X} is not a valid index'
            logger.debug('REST API error: ' + msg)
            return make_error_json(msg)
    else:
        try:
            obj = app.node.od[index][subindex]
        except Exception:
            msg = f'0x{subindex:02X} not a valid subindex for index 0x{index:04X}'
            logger.debug('REST API error: ' + msg)
            return make_error_json(msg)

    if isinstance(obj, canopen.objectdictionary.Variable):
        value = app.node._on_sdo_read(index, subindex, obj)
        if obj.data_type in [DataType.DOMAIN, DataType.OCTET_STRING] and value is not None:
            # encode bytes data types for JSON
            value = base64.encodebytes(value).decode('utf-8')

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
        data['subindexes'] = {subindex: _object_to_dict(index, subindex) for subindex in obj}
    else:
        data['object_type'] = 'RECORD'
        data['subindexes'] = {subindex: _object_to_dict(index, subindex) for subindex in obj}

    return data


@rest_api.app.route('/od-all', methods=['GET'])
def get_all_object():
    data = {}
    for index in app.od:
        if index < 0x1000:
            continue
        data[index] = _object_to_dict(index)
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


@rest_api.app.route('/daemons')
def daemons_template():
    return render_olaf_template('daemons.html', name='External Daemons')


@rest_api.app.route('/oresat-configs')
def oresat_configs_template():
    return render_olaf_template('oresat_configs.html', name='OreSat Configs')
