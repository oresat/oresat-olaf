Other
=====

Logger
------

OLAF makes use of the `loguru`_ library internally, so an app should make use its logger
as needed.

**How to:**

.. code-block::

   from loguru import logger

   logger.error('error message')

.. _loguru: https://github.com/Delgan/loguru

Argument Parser
---------------

.. autodata:: olaf.app_args_parser
   :annotation:

.. autofunction:: olaf.parse_app_args

**How to:**

.. code-block::

    from argparse import ArgumentParser

    from olaf import app_args_parser, parse_app_args

    parser = ArgumentParser(parents=[app_args_parser])
    parser.add_argument('-m', help='message')
    ...
    # add arg
    ...
    args = parser.parse_args()
    parse_app_args(args)

    # use these as needed
    can_interface = args.interface
    node_id = args.node_id
