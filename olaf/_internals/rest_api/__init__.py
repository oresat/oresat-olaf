"""OLAF REST API for testing and integration."""

import base64
import logging
import os
import shutil
from pathlib import Path
from threading import Thread
from typing import Union

import canopen
from flask import Flask, jsonify, render_template, request, send_from_directory
from loguru import logger
from oresat_configs import OreSatId
from werkzeug.serving import make_server

from ...common import natsorted
from ..app import app

DATA_TYPE_NAMES = {
    canopen.objectdictionary.BOOLEAN: "BOOLEAN",
    canopen.objectdictionary.INTEGER8: "INTEGER8",
    canopen.objectdictionary.INTEGER16: "INTEGER16",
    canopen.objectdictionary.INTEGER32: "INTEGER32",
    canopen.objectdictionary.INTEGER64: "INTEGER64",
    canopen.objectdictionary.UNSIGNED8: "UNSIGNED8",
    canopen.objectdictionary.UNSIGNED16: "UNSIGNED16",
    canopen.objectdictionary.UNSIGNED32: "UNSIGNED32",
    canopen.objectdictionary.UNSIGNED64: "UNSIGNED64",
    canopen.objectdictionary.REAL32: "REAL32",
    canopen.objectdictionary.REAL64: "REAL64",
    canopen.objectdictionary.VISIBLE_STRING: "VISIBLE_STRING",
    canopen.objectdictionary.OCTET_STRING: "OCTET_STRING",
    canopen.objectdictionary.DOMAIN: "DOMAIN",
}

BYTES_TYPES = [
    canopen.objectdictionary.OCTET_STRING,
    canopen.objectdictionary.DOMAIN,
]


class RestAPI:
    """
    An optional Flask app for reading and writing values into the OD.

    Use the global ``olaf.rest_api`` object.
    """

    _PATH = os.path.dirname(os.path.abspath(__file__))
    _TEMPLATE_DIR = "/tmp/oresat/templates"

    def __init__(self):
        self.app = Flask(
            "OLAF", template_folder=self._TEMPLATE_DIR, static_folder=f"{self._PATH}/static"
        )
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        self._thread = Thread(target=self._run)
        self._server = None
        self._ctx = None
        Path(self._TEMPLATE_DIR).mkdir(parents=True, exist_ok=True)

        # add all core templates
        for i in os.listdir(f"{self._PATH}/templates"):
            self.add_template(f"{self._PATH}/templates/{i}")

    def setup(self, address: str, port: int):
        """Setup the REST API thread"""

        self._server = make_server(address, port, self.app)

    def start(self):
        """Start the REST API thread"""

        logger.info("starting rest api")
        self._ctx = self.app.app_context()
        self._ctx.push()
        self._thread.start()

    def _run(self):
        self._server.serve_forever()

    def stop(self):
        """Stop the REST API thread"""

        logger.info("stopping rest api")
        if self._server is not None:
            self._server.shutdown()
        if self._thread.is_alive():
            self._thread.join()

    def add_template(self, template_path: str):
        """
        Add a Flask template to common templates dir. All templates must be in the same directory.

        Parameters
        ----------
        template_path: str
            Path to the template file to add.
        """

        shutil.copy(template_path, self._TEMPLATE_DIR)


def render_olaf_template(template: str, name: str):
    """
    Render a standard OLAF template.

    Parameters
    ----------
    template: str
        Template file name.
    name: str
        Nice name for the template.
    """

    os_id = app.od["satellite_id"].value
    os_ver_str = OreSatId(os_id).name[6:].replace("_", ".")
    title = f"OreSat{os_ver_str} {app.od.device_information.product_name}"
    return render_template(template, title=title, name=name)


def make_error_json(error: Union[str, Exception]) -> str:
    """
    Make the stand error json message for the REST API

    Parameters
    ----------
    error: str, Exception
        The error message

    Returns
    -------
    str
        The JSON error message
    """

    return jsonify({"error": str(error)})


rest_api = RestAPI()
"""The global instance of the REST API."""


@rest_api.app.route("/")
def root():
    """Render the root template."""

    routes = []
    for rule in rest_api.app.url_map.iter_rules():
        route = str(rule)
        if (
            not route.startswith("/static/")
            and not route.startswith("/od/")
            and route not in ["/", "/favicon.ico", "/od-all", "/bus"]
        ):
            routes.append(str(rule))

    routes = natsorted(routes)

    os_id = app.od["satellite_id"].value
    os_ver_str = OreSatId(os_id).name[6:].replace("_", ".")
    title = f"OreSat{os_ver_str} {app.od.device_information.product_name}"
    return render_template("root.html", title=title, routes=routes)


@rest_api.app.route("/favicon.ico")
def favicon():
    """Pass the favicon.icon."""

    path = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(f"{path}/static", "favicon.ico")


def _json_value_to_value(data_type: int, json_value):
    """Convert JSON value to real OD value to bytes for SDO callback"""

    value = json_value

    if data_type == canopen.objectdictionary.BOOLEAN and not isinstance(json_value, bool):
        value = json_value.lower() == "true"
    elif data_type in canopen.objectdictionary.INTEGER_TYPES and not isinstance(json_value, int):
        value = int(json_value, 16) if json_value.startswith("0x") else int(json_value)
    elif data_type in canopen.objectdictionary.FLOAT_TYPES:
        value = float(json_value)
    elif data_type in BYTES_TYPES:
        try:
            value = base64.decodebytes(json_value.encode("utf-8"))
        except AttributeError:
            pass

    return value


@rest_api.app.route("/bus", methods=["GET"])
def can_bus():
    """Get CAN bus info."""

    return jsonify(
        {
            "channel": app.node.bus,
            "bitrate": app.od.bitrate // 1000,  # bps -> kpbs
            "status": app.node.bus_state,
        }
    )


@rest_api.app.route("/od/<index>/", methods=["GET", "PUT"])
def od_index_old(index: str):
    """Read or write a value from OD with only a index. For backward compactability."""

    return od_index(index)


@rest_api.app.route("/od/<index>/<subindex>/", methods=["GET", "PUT"])
def od_subindex_old(index: str, subindex: str):
    """Read or write a value from OD. For backward compactability."""

    return od_subindex(index, subindex)


@rest_api.app.route("/od/<index>", methods=["GET", "PUT"])
def od_index(index: str):
    """Read or write a value from OD with only a index."""

    try:
        if index.startswith("0x"):
            index = int(index, 16)  # type: ignore
        elif index[0] in "0123456789":
            index = int(index)  # type: ignore
    except ValueError:
        return make_error_json(f"invalid index {index}")

    try:
        obj = app.od[index]
    except KeyError:
        index_name = f"0x{index:X}" if isinstance(index, int) else index
        msg = f"no object at index {index_name}"
        logger.error(f"REST API error: {msg}")
        return make_error_json(msg)

    if request.method == "PUT":
        try:
            json_value = request.json["value"]

            # convert value from JSON to bytes for SDO callback
            value = _json_value_to_value(obj.data_type, json_value)
            raw = obj.encode_raw(value)

            app.node._on_sdo_write(index, None, obj, raw)  # pylint: disable=W0212
        except Exception as e:  # pylint: disable=W0718
            logger.error(f"REST API error: {e}")
            return make_error_json(str(e))

    return jsonify(_object_to_dict(index))


@rest_api.app.route("/od/<index>/<subindex>", methods=["GET", "PUT"])
def od_subindex(index: str, subindex: str):
    """Read or write a value from OD."""

    try:
        if index.startswith("0x"):
            index = int(index, 16)  # type: ignore
        elif index[0] in "0123456789":
            index = int(index)  # type: ignore

        if subindex.startswith("0x"):
            subindex = int(subindex, 16)  # type: ignore
        elif subindex[0] in "0123456789":
            subindex = int(subindex)  # type: ignore
    except ValueError:
        return make_error_json(f"invalid index {index} or subindex {subindex}")

    try:
        obj = app.od[index][subindex]
    except (KeyError, TypeError):
        index_name = f"0x{index:X}" if isinstance(index, int) else index
        subindex_name = f"0x{subindex:X}" if isinstance(subindex, int) else subindex
        msg = f"no object at index {index_name} subindex {subindex_name}"
        logger.error(f"REST API error: {msg}")
        return make_error_json(msg)

    if request.method == "PUT":
        try:
            json_value = request.json["value"]

            # convert value from JSON to bytes for SDO callback
            value = _json_value_to_value(obj.data_type, json_value)
            if obj.data_type in BYTES_TYPES:
                raw = value
            else:
                raw = obj.encode_raw(value)

            app.node._on_sdo_write(index, subindex, obj, raw)  # pylint: disable=W0212
        except Exception as e:  # pylint: disable=W0718
            logger.exception(f"REST API error: {e}")
            return make_error_json(str(e))

    return jsonify(_object_to_dict(index, subindex))


def _object_to_dict(
    index: Union[str, int],
    subindex: Union[str, int, None] = None,
    add_values: bool = True,
) -> dict:
    """
    Convert a OD object to a dictionary.

    Parameters
    ----------
    index: str, int
        The index of the object to convert.
    subindex: str, int
        Optional subindex of the object to convert.
    add_values: bool
        Add values (current and engineering value) to dict.

    Returns
    -------
    dict
        The object as a dictionary.
    """

    if subindex is None:
        try:
            obj = app.node.od[index]
        except KeyError:
            msg = f"0x{index:04X} is not a valid index"
            logger.debug("REST API error: " + msg)
            raise KeyError(msg)
    else:
        try:
            obj = app.node.od[index][subindex]
        except KeyError:
            msg = f"0x{subindex:02X} not a valid subindex for index 0x{index:04X}"
            logger.debug("REST API error: " + msg)
            raise KeyError(msg)

    if isinstance(obj, canopen.objectdictionary.Variable):
        value = app.node._on_sdo_read(index, subindex, obj)  # pylint: disable=W0212
        if obj.data_type in BYTES_TYPES and value is not None:
            # encode bytes data types for JSON
            try:
                value = base64.encodebytes(value).decode("utf-8")
            except TypeError:
                logger.error(f"object {obj.name} does not have bytes-like data")

    data = {
        "name": obj.name,
        "index": obj.index,
        "description": obj.description,
    }

    if isinstance(obj, canopen.objectdictionary.Variable):
        data["object_type"] = "VARIABLE"
        data["access_type"] = obj.access_type
        data["data_type"] = DATA_TYPE_NAMES[obj.data_type]
        if add_values:
            data["value"] = value
            data["eng_value"] = value  # always include, even when the same as value
        if obj.data_type in canopen.objectdictionary.INTEGER_TYPES:
            data["bit_definitions"] = obj.bit_definitions
            data["value_descriptions"] = obj.value_descriptions
            data["scale_factor"] = obj.factor
            if add_values:
                data["eng_value"] = obj.factor * value
        data["subindex"] = obj.subindex
        data["unit"] = obj.unit
        data["low_limit"] = obj.min or ""
        data["high_limit"] = obj.max or ""
    elif isinstance(obj, canopen.objectdictionary.Array):
        data["object_type"] = "ARRAY"
        data["subindexes"] = {sub: _object_to_dict(index, sub, add_values) for sub in obj}
    else:
        data["object_type"] = "RECORD"
        data["subindexes"] = {sub: _object_to_dict(index, sub, add_values) for sub in obj}

    return data


@rest_api.app.route("/od-all", methods=["GET"])
def get_all_object():
    """Get all object data as a one giant JSON."""
    data = {}
    for index in app.od:
        if index < 0x3000:
            continue
        data[index] = _object_to_dict(index, None, False)
    return data


@rest_api.app.route("/od")
def od_template():
    """Render the OD template."""
    return render_olaf_template("od.html", name="Object Dictionary")


@rest_api.app.route("/os-command")
def os_command_template():
    """Render the OS command template."""
    return render_olaf_template("os_command.html", name="OS Command")


@rest_api.app.route("/updater")
def updater_template():
    """Render the updater template."""
    return render_olaf_template("updater.html", name="Updater")


@rest_api.app.route("/fwrite")
def fwrite_template():
    """Render the fwrite cache template."""
    return render_olaf_template("fwrite.html", name="Fwrite Cache")


@rest_api.app.route("/fread")
def fread_template():
    """Render the fread cache template."""
    return render_olaf_template("fread.html", name="Fread Cache")


@rest_api.app.route("/logs")
def logs_template():
    """Render the logs template."""
    return render_olaf_template("logs.html", name="Logs")


@rest_api.app.route("/reset")
def reset_template():
    """Render the reset template."""
    return render_olaf_template("reset.html", name="Reset")
