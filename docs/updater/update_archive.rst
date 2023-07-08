Update Archive
==============

An update archive is tar file that will be used by an OreSat application
to update the Linux board the daemon is running on. The update maker will 
be used to generate these files.

Compression
-----------

Update files are a tar file compressed with xz. xz is used as it offers a great
compression ratio and the extra compression time doesn't matter, since the
update archive will be generated on a ground station server.

Tar Name
---------

The file name will follow filename standards for OreSat Linux Files with the 
keyword set to ``"update"``. 

**Example, a update to the GPS board**::

   gps_update_1612392143000.tar.xz

The date field in the filename will be used to determine the next file to used
as the oldest file is always run first.

Tar Contents
-------------

The update archive will **always** include a `instructions.txt` file. It can also
include Debian packages (``.deb`` files), Python packages (``.whl`` files), Bash
scripts (``.sh`` files), and other files to be used by Bash scripts as needed.

**Example contents of a update archive**::

    instructions.txt
    package1.deb
    package2.deb
    package3.deb
    bash_script1.sh
    bash_script2.sh
    bash_script3.sh
    py_package1.whl
    py_package2.whl

instructions.txt
----------------

`instructions.txt` contatins a JSON string with with a list of instruction
dictionaries with `type` and `items` fields. The instructions will be run in
order.

**Type values**:

* ``BASH_SCIPT`` - run a Bash script
* ``DPKG_INSTALL`` - install Debian package(s) using dpkg
* ``DPKG_REMOVE`` - remove Debian package(s) using dpkg
* ``DPKG_PURGE`` - purge Debian package(s) using dpkg
* ``PIP_INSTALL`` - install Python package(s) using pip
* ``PIP_UNINSTALL`` - uninstall Python package(s) using pip

**Example instructions.txt**::

    [
        {
            "type": "DPKG_INSTALL",
            "items": ["package1.deb"]
        },
        {
            "type": "BASH_SCIPT",
            "items": ["bash_script1.sh"]
        },
        {
            "type": "BASH_SCIPT",
            "items": ["bash_script2.sh"]
        },
        {
            "type": "DPKG_INSTALL",
            "items": ["package2.deb", "package3.deb"]
        },
        {
            "type": "DPKG_REMOVE",
            "items": ["package4"]
        },
        {
            "type": "BASH_SCIPT",
            "items": ["bash_script3.sh"]
        },
        {
            "type": "PIP_INSTALL",
            "items": ["py_package1.whl", "py_package2.whl"]
        },
        {
            "type": "PIP_UNINSTALL",
            "items": ["py_package3.whl"]
        },
        {
            "type": "DPKG_PURGE",
            "items": ["package5", "package6"]
        },
    ]
