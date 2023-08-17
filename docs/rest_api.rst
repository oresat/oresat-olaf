Rest API
========

OLAF includes an internal REST API using `Flask`_. The REST API is used to give insight into what
the OLAF app is doing during testing and system integration without using the CAN bus.

The REST API provides the ``/od/<index>/`` and ``/od/<index>/<subindex>/`` endpoints that will
call the internal SDO uploads / downloads for objects at that index and subindex.

View the EDS or DCF file to see what indexes and subindexes are available. Or get the output from
the ``/od-all`` endpoint.

.. note:: If a object is a DOMAIN (arbitrary binary data) type, the value will be encoded with 
   Base64 on a read and must be encoded on a write.

Reading a object from the OD
----------------------------

Read a variable at an index.

.. code:: bash
  
  $ curl -X GET localhost:8000/od/0x1000/
  {
    "access_type": "ro",
    "data_type": "UNSIGNED32",
    "name": "Device type",
    "object_type": "VARIABLE",
    "value": 0
  }

Read a record / array at an index.

.. code:: bash
  
  $ curl -X GET localhost:8000/od/0x1018/
  {
    "name": "Identity",
    "object_type": "RECORD",
    "subindexes": {
      "0": {
        "access_type": "const",
        "data_type": "UNSIGNED8",
        "name": "Highest sub-index supported",
        "object_type": "VARIABLE",
        "value": 4
      },
      "1": {
        "access_type": "ro",
        "data_type": "UNSIGNED32",
        "name": "Vendor-ID",
        "object_type": "VARIABLE",
        "value": 0
      },
      "2": {
        "access_type": "ro",
        "data_type": "UNSIGNED32",
        "name": "Product code",
        "object_type": "VARIABLE",
        "value": 0
      },
      "3": {
        "access_type": "ro",
        "data_type": "UNSIGNED32",
        "name": "Revision number",
        "object_type": "VARIABLE",
        "value": 0
      },
      "4": {
        "access_type": "ro",
        "data_type": "UNSIGNED32",
        "name": "Serial number",
        "object_type": "VARIABLE",
        "value": 0
      }
    }
  }

Read a variable at an index and subindex.

.. code:: bash
  
  $ curl -X GET localhost:8000/od/0x1018/0x01/
  {
    "access_type": "ro",
    "data_type": "UNSIGNED32",
    "name": "Device type",
    "object_type": "VARIABLE",
    "value": 0
  }

Writing a value to object in the OD
-----------------------------------

When writing to an object the value is always read back.

.. note:: The value writen must match the datatype. You cannot write ``"2"`` to a integer object.

Write a value to a variable at an index.

.. code:: bash
  
  $ curl -X PUT localhost:8000/od/0x6000/ --header 'content-type: application/json' --data '{"value": 0}'
  {
    "access_type": "ro",
    "data_type": "UNSIGNED32",
    "name": "Device type",
    "object_type": "VARIABLE",
    "value": 2
  }

Write a value to a variable at an index and subindex.

.. code:: bash
  
  $ curl -X PUT localhost:8000/od/0x1018/0x01/ --header 'content-type: application/json' --data '{"value":  2}'
  {
    "access_type": "ro",
    "data_type": "UNSIGNED32",
    "name": "Device type",
    "object_type": "VARIABLE",
    "value": 2
  }

Errors
------

When a invalid read or write happens, the reponse have ``"error"`` feild.

.. code:: bash
  
  $ curl -X PUT localhost:8000/od/0x9000/ --header 'content-type: application/json' --data '{"value":  1}'
  {
    "error": "index 0x9000 does not exist"
  }

.. _Flask: https://github.com/pallets/flask
