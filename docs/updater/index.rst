Updater
=======

An OreSat application has the ability to update the board it is running on thru update archives.

.. toctree::
   :maxdepth: 2
   :caption: Update Archive

   update_archive

Basics
------

- Sending a update archive to the node will **not** trigger an update, only 
  when the update subindex in the object dictionary is set an update will start.
- Can also generate status file that can be used to make future updates and to
  know what is install on the board.
- If a update fails the update file cache will be clear as it is assume all
  future updates require older updates.

States
------

.. autoclass:: olaf._internals.updater.UpdaterState
   :members:
   :member-order: bysource
   :noindex:
