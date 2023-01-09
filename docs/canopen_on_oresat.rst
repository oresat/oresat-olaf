CANopen on OreSat
=================

OD (Object Dictionary)
----------------------

- All common objects found on all boards, all firmware boards, and/or all Linux
  boards are in the ``0x3000`` to ``0x5FFF`` range.
- All unique objects for a board are place in the >= ``0x6000`` range.

Nodes
-----

All nodes (CANopen device on CAN bus) can be a master node or regular node. On
OreSat, the master node is the C3.

**On OreSat** (not can CANopen standard), all nodes will use the place of 4
nodes. Example, If an OreSat card is assigned ``NODE-ID`` of ``0x40``, there
will never be a nodes with ``NODE-IDs`` of ``0x41``, ``0x42``, or ``0x43``. 
This allow all nodes on OreSat to use 4x PDO.

The master node for OreSat is the C3 and it has ``NODE-ID`` of ``0x01``.

All other ``NODE-IDs`` are multiples of ``0x04``; e.g: ``0x04``, ``0x08``, 
``0x12``, etc. And they use the PDOs of +1, +2, +3 to their ``NODE-IDs``. 

An example of board with ``NODE-ID`` of ``0x4``:

- No nodes with ``NODE-ID`` of ``0x05``, ``0x06``, ``0x07`` will exist on
  OreSat.
- Can use the following 16 TPDOs: ``0x184``, ``0x284``, ``0x384``, ``0x484``, 
  ``0x185``, ``0x285``, ``0x385``, ``0x485``, ``0x186``, ``0x286``, ``0x386``,
  ``0x486``, ``0x187``, ``0x287``, ``0x387``, and ``0x487``.
- Can use the following 16 RPDOs: ``0x204``, ``0x304``, ``0x404``, ``0x504``, 
  ``0x205``, ``0x305``, ``0x405``, ``0x505``, ``0x206``, ``0x306``, ``0x406``, 
  ``0x506``, ``0x207``, ``0x307``, ``0x407``, and ``0x507``.

Time Sync
---------

The time sync message on OreSat uses the ECSS SCET format with the Unix 
timestamp as the epoch.

ECSS SCET definition
********************

.. code-block::

    struct {
        unsigned 32 Coarse Time
        unsigned 24 Fine Time (sub seconds)
    } SCET

On OreSat the SCET value is a uint64 with Coarse Time first 4 bytes,
followed by the Fine Time 3 bytes, and the 8th byte as padding.

Time Syncing
************

Time syncing is handle by the C3 and the GPS board. The TPDO with ``COB-ID`` of
``0x181`` is reserved to be the Time Sync TPDO. Both the C3 and GPS board can 
sent it. All nodes that care about time, except the node that sent the Time 
Sync TPDO, will sync their clocks to the time in the Time Sync TPDO when it is
recieved. 

The C3 has an RTC (Real Time Clock) and the GPS board has a GPS reciever and 
will set it's system time to the GPS time in GPS messages.

The GPS board will only send the Time Sync TPDO, if has sync it's system time
to GPS time and it recieves a SYNC message from the C3. So, either way the C3
has full control when all clocks are sync'd. The C3 can just send out the Time
Sync TPDO (it will use the time from it's RTC) or request it from the GPS
board, if the GPS board is on.
