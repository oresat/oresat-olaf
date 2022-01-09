Other
=====

Logger
------

OreSat Linux Node make use of the `loguru`_ library internally, so node should make use its logger
as needed.

**How to:**

.. code-block::

   from loguru import logger

   logger.error('error message')

.. _loguru: https://github.com/Delgan/loguru

Argument Parser
---------------

.. autodata:: oresat_linux_node.node_args_parser
   :annotation:

.. autofunction:: oresat_linux_node.parse_node_args

**How to:**

.. code-block::

    from argparse import ArgumentParser

    from oresat_linux_node import node_args_parser, parse_node_args

    parser = ArgumentParser(parents=[node_args_parser])
    parser.add_argument('-m', help='message')
    ...
    # add arg
    ...
    args = parser.parse_args()
    parse_node_args(args)

    # use these as needed
    can_interface = args.interface
    node_id = args.node_id
