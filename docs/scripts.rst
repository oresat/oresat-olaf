OLAF Scripts
============

The ``oresat-olaf`` Python package comes with useful generic CANopen and OLAF
specific scripts.

All script use python's `argparse`_ module, so they all have ``-h`` and
``--help`` flags for a full list of arguments


Generic CANopen Scripts

- ``olaf-sdo-transfer``: Read or write data to a node's OD using an SDO.
- ``olaf-sync``: Send an CANopen SYNC message on CAN bus.


OLAF Specific Scripts

- ``olaf-file-transfer``: Read or write a file to OLAF app.
- ``olaf-os-command``: Make a node run a OS Command.
- ``olaf-system-info``: Get the system info from an OLAF app.
- ``olaf-new-eds``: Make a new EDS file for an OLAF app.

.. _argparse: https://docs.python.org/3/library/argparse.html
