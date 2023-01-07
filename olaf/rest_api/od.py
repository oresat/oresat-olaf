import os
import base64
from enum import IntEnum

import canopen
from flask import Blueprint, render_template, jsonify, request

from .. import app


od_bp = Blueprint('od', __name__, template_folder='templates')


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


@od_bp.route('/od')
def od_template():

    return render_template('od.html', title=os.uname()[1])


@od_bp.route('/od/<index>/', methods=['GET', 'PUT'])
def od_index(index: str):

    index = int(index, 16) if index.startswith('0x') else int(index)

    if request.method == 'PUT':
        raw = request.json['value']
        data_type = app.od[index].data_type
        if data_type == DataType.DOMAIN:
            app.node.sdo[index].raw = base64.decodebytes(raw.encode('utf-8'))
        else:
            app.node.sdo[index].phys = raw_to_value(data_type, raw)

    return jsonify(object_to_json(index))


@od_bp.route('/od/<index>/<subindex>/', methods=['GET', 'PUT'])
def od_subindex(index: str, subindex: str):

    index = int(index, 16) if index.startswith('0x') else int(index)
    subindex = int(subindex, 16) if subindex.startswith('0x') else int(subindex)

    if request.method == 'PUT':
        raw = request.json['value']
        data_type = app.od[index][subindex].data_type
        if data_type == DataType.DOMAIN:
            app.node.sdo[index][subindex].raw = base64.decodebytes(raw.encode('utf-8'))
        else:
            app.node.sdo[index][subindex].phys = raw_to_value(data_type, raw)

    return jsonify(object_to_json(index, subindex))


def raw_to_value(data_type: DataType, raw: str):
    value = None

    if data_type == DataType.BOOLEAN:
        value = True if raw.lower() == 'true' else False
    elif data_type in [DataType.INTEGER8, DataType.INTEGER16, DataType.INTEGER32,
                       DataType.INTEGER64, DataType.UNSIGNED8, DataType.UNSIGNED16,
                       DataType.UNSIGNED32, DataType.UNSIGNED64]:
        value = int(value, 16) if value.startswith('0x') else int(value)
    elif data_type in [DataType.REAL32, DataType.REAL64]:
        value = float(raw)
    else:
        value = raw

    return value


def object_to_json(index: int, subindex: int = None) -> dict:

    if subindex is None:
        try:
            obj = app.od[index]
            if isinstance(obj, canopen.objectdictionary.Variable):
                if obj.data_type == DataType.DOMAIN:
                    raw = app.node.sdo[index].raw
                    value = base64.encodebytes(raw).decode('utf-8')
                else:
                    value = app.node.sdo[index].phys
        except Exception:
            return {'error': f'0x{index:04X} is not a valid index'}
    else:
        try:
            obj = app.od[index][subindex]
            if obj.data_type == DataType.DOMAIN:
                raw = app.node.sdo[index][subindex].raw
                value = base64.encodebytes(raw).decode('utf-8')
            else:
                value = app.node.sdo[index][subindex].phys
        except Exception:
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
        data['subindexes'] = len(obj)
    else:
        data['object_type'] = 'RECORD'
        data['subindexes'] = len(obj)

    return data
