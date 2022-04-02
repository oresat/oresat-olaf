Example App
===========

An example OLAF app that uses a virtual CAN bus.

Run the example app
-------------------

-   Clone the git repo 

    .. code-block:: text

        $ git clone https://github.com/oresat/oresat-olaf
        $ cd oresat-olaf

-   Make a virtual CAN bus
        
    .. code-block:: text

        $ sudo ip link add dev vcan0 type vcan
        $ sudo ip link set vcan0 up

-   Swap to the ``example_app`` directory

    .. code-block:: text

        $ cd example_app

-   Install dependencies 

    .. code-block:: text

      $ pip install -r requirements.txt

-   Run example

    .. code-block:: text

      $ python -m example_app
