OLAF (OreSat Linux App Framework)
=================================

.. image:: https://img.shields.io/github/license/oresat/oresat-olaf
   :target: https://github.com/oresat/oresat-olaf/blob/master/LICENSE
   :alt: License
.. image:: https://img.shields.io/github/issues/oresat/oresat-olaf
   :target: https://github.com/oresat/oresat-olaf/issues
   :alt: Issues
.. image:: https://readthedocs.org/projects/oresat-olaf/badge/?version=latest
   :target: https://oresat-olaf.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. image:: https://github.com/oresat/oresat-olaf/actions/workflows/tests.yaml/badge.svg
   :target: https://github.com/oresat/oresat-olaf/actions/workflows/tests.yaml
   :alt: Test Status

A pythonic CANopen application framework for all OreSat Linux boards. Built
ontop on `python-canopen`_. It is designed to handle all the common OreSat
`CANopen`_ Node functionality including support for `ECSS CANBus Extended
Protocol`_, file transfer over CAN, and updating the Linux board.

Installing
----------

Install using pip:

.. code-block:: text

   $ pip install oresat-olaf

.. References
.. _unittest: https://docs.python.org/3/library/unittest.html#module-unittest
.. _sphinx: https://www.sphinx-doc.org/en/master/
.. _python-canopen: https://github.com/christiansandberg/canopen
.. _CANopen: https://www.can-cia.org/canopen
.. _ECSS CANBus Extended Protocol: https://ecss.nl/standard/ecss-e-st-50-15c-space-engineering-canbus-extension-protocol-1-may-2015/
