OreSat File
===========

OLAF only support file in the ``card_keyword_timestamp.extension`` or ``card_keyword_timestamp``
format where:

- The ``card`` field is the name of card it is for or the name of card it was made on; e.g.:
  ``gps``, ``star-tracker``, etc.
- The ``keyword`` field is a useful keyword for the file.

  - Use ``-`` to seperate multiple keywords.
  - The keyword ``update`` is reserved for updates.

- The ``timestamp`` field is the unix timestamp in milliseconds when the file was made.
- The ``.extension`` field is the optional extension. Can also be multiple extensions, e.g.:
  ``.tar.gz``.

All fields should not contain ``_`` as it is used to seperate the fields.


Reasoning behind naming scheme:

- Between the ``card``, ``keyword``, and ``timestamp`` fields all file names should be unique.
- When a file is upload to the C3 from the UniClOGS, the C3 can use card field can be used to
  figure out if the file is for it or what card to send the file to over the CAN bus.
- When file are download from the C3 to UniClOGS, all 3 fields can be used to figure out what card
  the file originated from, what it is, and when it was made.

Examples:

- ``gps_update_1688791896103.tar.xz``
- ``star-tracker_capture_1688791896103.bmp.gz``
- ``cfc_capture_1688791896103.bmp.gz``
- ``c3_logs_1688791896103.txt.xz``


.. autofunction:: olaf.new_oresat_file

.. autoclass:: olaf.OreSatFile
   :class-doc-from: both
   :members:
   :member-order: bysource
