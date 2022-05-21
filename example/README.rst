OLAF Example App
================

An example OLAF app that uses a virtual CAN bus.

Setup
-----

-   Clone the git repo::

    $ git clone https://github.com/oresat/oresat-olaf
    $ cd oresat-olaf

-   Make a virtual CAN bus::

    $ sudo ip link add dev vcan0 type vcan
    $ sudo ip link set vcan0 up

-   Swap to the ``example`` directory::

    $ cd example


Run without docker compose
--------------------------

-   Install dependencies::

    $ pip install -r requirements.txt

-   Run example::

    $ python -m example_app


Run with docker compose
-----------------------

-   Build docker image::

    $ docker-compose build

-   Run with docker::

    $ docker-compose run example-app

Notes for example_dev:

Use pip to install OLAF with:
 $ pip install oresat-olaf

In order to install the required python packages, you should also use pip:
$ pip install -r requirements-dev.txt

To execute the main OLAF app, simply execute run.py with python3:
python3 run.py

To run the example application with the example resource, clone the example_dev branch and navigate to the example directory, the enter the following command:
python3 -m example_app

If a physical CAN bus is not available, output can easily be seen using candump. Candump is part of can-utils. Install can-utils using your system’s package manager, then set up the virtual CAN bus using the vcan.sh script provided with OLAF. Then, set up a candump of vcan0 and open a new terminal window to execute the desired OLAF program. To access the read and write functions over the virtual CAN bus, you can use the sdo_transfer.py script. The example resource has read and write callbacks at index 0x1AOF, subindice 0x1 for writes, and subindice 0x2 for reads. The example resource will take a picture with a given filename when written to, and return the filepath in ASCII hex when read from. Note that a functional camera must be present in your USB devices for the camera functions to work. Setting those up on your system is outside the scope of this project.
