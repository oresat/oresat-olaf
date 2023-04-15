CANopen Basics
==============

.. note:: 

  This only goes over the basics of CANopen for what is need to work on a
  OreSat device. For the full standards, see the `CAN in Automation (CiA)`_
  website.

`CANopen`_ is a message protocal for `CAN`_ messages on a `CAN`_ bus by 
`CAN in Automation (CiA)`_.

Nodes
-----

A node is a CANopen device. All nodes can be a master node or regular node.

All nodes will have an unique ``NODE-ID``, between ``0x01`` and ``0x7F``.

Only the master node can use SDO to read or write values another node's OD.

OD (Object Dictionary)
----------------------

The data structure / API that hold all data for CANopen node.

Objects can have indexes and subindex.
Valid indexes range from ``0x1000`` to ``0x8000`` and valid subindex range from
``0x00`` to ``0xFF``.

Objects at an indexes can be Variables, Arrays, or Records (aka structs).  Only
Variables can be object with a subindex. An Array or Record will have one or
more Variables as subidexes. Subindex ``0x00`` of all Arrays and Records will
be the highest index of the Array or Record.

Indexes can be divide into 3 groups: Manidtory, Manufacture, and Optional.

- Manidtory Objects (``0x1000``, ``0x1001``, ``0x1018``) are requeired index 
  for all nodes.
- Manufacture Objects (``0x2000`` to ``0x5FFF``) are objects addded by
  manufacturer.
- Optional Objects (``0x1000`` to ``0x1FFF`` and ``0x6000`` to ``0x8000``) are
  objects added by user.

Files
-----

Both EDS and DCF are used to document and configure a CANopen device as well
as generate code for the OD for software / firmware.

The ``eds-editor`` GUI from the `eds-utils`_ project can be used to edit,
view, manipulate EDS and DCF files.

EDS (Electronic Data Sheet)
***************************

An EDS file a ``.conf`` or ``.ini`` like configuration file for describing the
OD. It is used as the documentation and configuration file of a device.

DCF (Device Configure File)
***************************

A DCF file is mostly a EDS file with a extra section for device configuration
like ``NODE-ID``, node name, and other node unique things.

A EDS is general file for a device and is used to generate the DCF. The DCF is
used when the device is on an actual production CAN bus. 

The main benefit of DCF is if there are multiple of the exact same device on 
the CAN bus, they all will have an unique DCF that was made from the same EDS 
file. 

Messages
--------

``COB-ID`` refers to 1 byte id part of a CAN message. CANopen nodes use the 
``COB-ID`` to id all messages.

Heartbeat
*********

All node send out a 1 byte heartbeat message with a ``COB-ID`` of
``0x700 + NODE-ID``.

The master node can use the heartbeat byte message to confirm what boards are
on and in a good state.

SDO (Service Data Object)
*************************

SDO allow the master node to read or write object from or to another node's OD.

SDO are the only messages that span over multiple CAN message, as the value 
that is being read or written can be any length as defined by OD.

SDO request messages use a ``COB-ID`` of ``0x580 + NODE-ID`` of the node the
master node is reading from or writing to. SDO response messages use a 
``COB-ID`` of ``0x600 + NODE-ID`` of the node the master node is reading from
or writing to.

PDO (Product Data Object)
*************************

PDOs are producer / consumer message, they don't not care if the node is a
master node or a regular node.

There are two type of PDOs: TPDO (Transmit PDO) and RPDO (Recieve PDO).
A node can produce data using TPDO and consume data using RPDO.

All PDOs are 1 to 8 byte message of mapped data from/to the OD.

Both RPDO and TPDO can be set up to be sent out every X SYNC message or on a
timer every X ms.

All nodes get 4 TPDOs and RPDOs by default, TPDO ``COB-ID`` are 
``0x180 + NODE-ID``, ``0x280 + NODE-ID``, ``0x380 + NODE-ID``, 
``0x480 + NODE-ID``. RPDO ``COB-ID`` are ``0x200 + NODE-ID``, 
``0x300 + NODE-ID``, ``0x400 + NODE-ID``, ``0x500 + NODE-ID``.

So a board with NODE-ID 0x4 can use the following 4 ``COB-ID`` for it's TPDOs:
``0x184``, ``0x284``, ``0x384``, ``0x484`` and 4 ``COB-ID`` for it's RPDOs:
``0x204``, ``0x304``, ``0x404``, ``0x504``.

SYNC
****

A message that TPDO can be configure to response to after every X occuraces.
A SYNC message always has ``COB-ID`` of ``0x80`` with no payload.

.. _CANopen: https://en.wikipedia.org/wiki/CANopen
.. _CAN: https://en.wikipedia.org/wiki/CAN
.. _CAN in Automation (CiA): https://can-cia.org/
.. _eds-utils: https://github.com/oresat/eds-utils
