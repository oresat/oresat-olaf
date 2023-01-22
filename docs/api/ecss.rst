ECSS
====

ECSS Space engineering CANbus extension protocol

SpaceCraft Elapsed Time (SCET)

.. code-block::

    struct {
        unsigned 32 Coarse Time
        unsigned 24 Fine Time (sub seconds)
    } SCET


Spacecraft Universal Time Coordinated (UTC)

.. code-block::

    struct {
        unsigned 16 Day
        unsigned 32 ms of day
        unsigned 16 submilliseconds of ms
    } UTC


.. autofunction:: olaf.scet_int_from_time

.. autofunction:: olaf.scet_int_to_time

.. autofunction:: olaf.utc_int_from_time

.. autofunction:: olaf.utc_int_to_time
