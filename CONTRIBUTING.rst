Contributing to OLAF
====================

Reporting bugs
--------------

Post your issue to `GitHub Issues`_ with the ``bug`` tag.

Include the following information in your post:

-   Describe what you expected to happen.
-   If possible, include a reproducible example to help identify the issue. 
-   Describe what actually happened. Include the full traceback if there
    was an exception.

Working on issues
-----------------

If there is not an open issue for what you want to submit, please open one 
for discussion before working on a issue and assigned yourself to it. You can
work on any issue that doesn't have a person already assigned to it. No need
to ask if you can work on an issue that interests you, but feel free to reach
out the the author if you need more info on the task.


First time setup
----------------

-   Clone the repository.

    .. code-block:: bash

        $ git clone https://github.com/oresat/oresat-olaf
        $ cd oresat-olaf

-   Install the development dependencies.

    .. code-block:: bash

        $ pip install -r requirements.txt

-   Install ``can-utils`` package for your system. This will give access to the
    ``candump`` command which will display all message on the CAN bus.

-   Make a virtual CAN bus. **Note** this will have to remade if the system is
    restarted.

    .. code-block:: bash

        $ sudo ip link add dev vcan0 type vcan
        $ sudo ip link set vcan0 up

-   Building local Docker image (optional)

    .. code-block:: bash

        $ docker build -t oresat-olaf .


How to run OLAF
---------------

Use ``run.py`` for quick testing. Use ``^C`` (hit Control and C keys) to stop
OLAF. Change the args after ``run.py`` as needed (``-h`` flag will print help
menu).

To run wthout docker

.. code-block:: bash

    $ ./run.py -v

Or to run with docker (if the docker image was built)

.. code-block:: bash

    $ docker run --rm -it -w /olaf -v `pwd`/:/olaf --network host oresat-olaf ./run.py -v

To see traffic on CAN bus, in another terminal use `candump`

.. code-block:: bash

    $ canump vcan0       
    vcan0  77C   [1]  7F
    vcan0  77C   [1]  7F
    vcan0  2FC   [2]  00 00
    vcan0  1FC   [6]  25 12 00 00 00 00
    vcan0  77C   [1]  05
    vcan0  77C   [1]  05
    vcan0  77C   [1]  05
    vcan0  77C   [1]  05
    vcan0  77C   [1]  05
    vcan0  2FC   [2]  00 00
    vcan0  77C   [1]  05
    ...


The scripts in ``/olaf/scripts`` can be used to interact with OLAF, e.g. read
/ write values to/from Object Dictionary, file transfer, bash commands over CAN
bus, etc.


Start coding
------------

-   Create a branch to identify the issue you would like to work on. If
    you're submitting a bug or documentation fix, branch off of the
    ``master`` branch and follow the naming scheme of "number-description"
    where number is the issue number and description is a one or two 
    word description. Example branch name would be ``15-more-unittests``.

    .. code-block:: bash

        $ git pull
        $ git checkout -b your-branch-name

-   Using your favorite IDE or text editor, make your changes, commit your work
    as you go.

-   Push your commits to your branch on GitHub.

    .. code-block:: bash

        $ git push --set-upstream your-branch-name

-   Once done `create a pull request`_. Link to the issue being addressed with 
    ``fixes #123`` in the pull request.


Running unit tests
------------------

Run the test with python's `unittest`_.

.. code-block:: bash

    $ python -m unittest


Running test coverage
---------------------

Generating a report of lines that do not have test coverage can indicate
where to start contributing. Run `unittest`_ using `coverage`_ and
generate a report.

.. code-block:: bash

    $ pip install coverage
    $ coverage run -m unittest
    $ coverage html

Open ``htmlcov/index.html`` in your browser to explore the report.


Building docs
-------------

Build the docs using `Sphinx`_.

.. code-block:: bash

    $ pip install -r requirements.txt
    $ cd docs
    $ make html

Open ``build/html/index.html`` in your browser to view the docs.

.. _GitHub Issues: https://github.com/oresat/oresat-olaf/issues
.. _create a pull request: https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request
.. _unittest: https://docs.python.org/3/library/unittest.html#module-unittest
.. _coverage: https://coverage.readthedocs.io
.. _Sphinx: https://www.sphinx-doc.orgttps://dont-be-afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-    your-changes/en/master/
