Example App
===========

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

    $ docker-compose run oresat-example-app
