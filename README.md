# OreSat Linux Node

[![License](https://img.shields.io/github/license/oresat/oresat-linux-node)](./LICENSE)
[![Issues](https://img.shields.io/github/issues/oresat/oresat-linux-node)](https://github.com/oresat/oresat-linux-node/issues)
[![Docs](https://readthedocs.org/projects/oresat-linux-node/badge/?version=latest)](https://oresat-linux-node.readthedocs.io/en/latest/?badge=latest)
[![Tests](https://github.com/oresat/oresat-linux-node/actions/workflows/tests.yaml/badge.svg)](https://github.com/oresat/oresat-linux-node/actions/workflows/tests.yaml)

A pythonic framework for all OreSat Linux boards applications build ontop on
[python-canopen]. It is designed to handle all the common OreSat [CANopen] Node
functionality including support for [ECSS CANBus Extended Protocal], file
transfer, and updating the Linux board.

## Examples

See examples in `examples/`

To run the `examples/example_node.py` example:

- Install dependencies `$ pip install -r requirements.txt`
- Make a virtual CAN bus `$ sudo ./scripts/vcan.sh`
- `$ cd examples`
- Run example `$ python example_node.py`

<!-- References -->
[python-canopen]:https://github.com/christiansandberg/canopen
[CANopen]:https://www.can-cia.org/canopen
[ECSS CANBus Extended Protocal]:https://ecss.nl/standard/ecss-e-st-50-15c-space-engineering-canbus-extension-protocol-1-may-2015/
