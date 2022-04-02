# OLAF (OreSat Linux App Framework)

[![License](https://img.shields.io/github/license/oresat/oresat-olaf)](./LICENSE)
[![Issues](https://img.shields.io/github/issues/oresat/oresat-olaf)](https://github.com/oresat/oresat-olaf/issues)
[![Docs](https://readthedocs.org/projects/oresat-olaf/badge/?version=latest)](https://oresat-olaf.readthedocs.io/en/latest/?badge=latest)
[![Tests](https://github.com/oresat/oresat-olaf/actions/workflows/tests.yaml/badge.svg)](https://github.com/oresat/oresat-olaf/actions/workflows/tests.yaml)

A pythonic CANopen application framework for all OreSat Linux boards. Built
ontop on [python-canopen]. It is designed to handle all the common OreSat
[CANopen] Node functionality including support for [ECSS CANBus Extended
Protocol], file transfer over CAN, and updating the Linux board.

## Installing

Install using pip:

`$ pip install oresat-olaf`

## Example App

See [example/README.md](example/README.md)

## Unit Tests

OreSat Linux App makes use of Python's [unittest] framework.

To run unit tests `$ python -m unittest`

## Docs

OreSat Linux App uses [sphinx] for documentation.

To build docs:

- Install dependencies `$ pip install -r requirements-dev.txt`
- Build docs `make -C docs html`
- Open `docs/build/html/index.html` in a web browser

<!-- References -->
[unittest]:https://docs.python.org/3/library/unittest.html#module-unittest
[sphinx]:https://www.sphinx-doc.org/en/master/
[python-canopen]:https://github.com/christiansandberg/canopen
[CANopen]:https://www.can-cia.org/canopen
[ECSS CANBus Extended Protocol]:https://ecss.nl/standard/ecss-e-st-50-15c-space-engineering-canbus-extension-protocol-1-may-2015/
