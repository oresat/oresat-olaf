Contributing to OLAF
====================

When you have a question
------------------------

Post your question to `GitHub issues`_ with the ``question`` tag.

Reporting issues
----------------

Post your issue to `GitHub issues`_ with the ``bug`` tag.

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

    .. code-block:: text

        $ git clone https://github.com/oresat/oresat-olaf
        $ cd oresat-olaf

-   Install the development dependencies.

    .. code-block:: text

        $ pip install -r requirements-dev.txt


Start coding
------------

-   Create a branch to identify the issue you would like to work on. If
    you're submitting a bug or documentation fix, branch off of the
    ``master`` branch and follow the naming scheme of "number-description"
    where number is the issue number and description is a one or two 
    word description. Example branch name would be "15-more-unittests"

    .. code-block:: text

        $ git pull
        $ git checkout -b your-branch-name

-   Make a virtual CAN bus.

    .. code-block:: text

        $ sudo ip link add dev vcan0 type vcan
        $ sudo ip link set vcan0 up

-   Using your favorite editor, make your changes, commit your work as you go.
-   Push your commits to your fork on GitHub.

    .. code-block:: text

        $ git push --set-upstream your-branch-name

-   Once done `create a pull request`_. Link to the issue being addressed with 
    ``fixes #123`` in the pull request.


Running unit tests
------------------

Run the test with python's `unittest`_.

.. code-block:: text

    $ python -m unittest


Running test coverage
---------------------

Generating a report of lines that do not have test coverage can indicate
where to start contributing. Run `unittest`_ using `coverage`_ and
generate a report.

.. code-block:: text

    $ pip install coverage
    $ coverage run -m unittest
    $ coverage html

Open ``htmlcov/index.html`` in your browser to explore the report.


Building docs
-------------

Build the docs using `Sphinx`_.

.. code-block:: text

    $ pip install -r requirements-dev.txt
    $ cd docs
    $ make html

Open ``build/html/index.html`` in your browser to view the docs.

.. _GitHub issues: https://github.com/oresat/oresat-olaf/issues
.. _create a pull request: https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request
.. _unittest: https://docs.python.org/3/library/unittest.html#module-unittest
.. _coverage: https://coverage.readthedocs.io
.. _Sphinx: https://www.sphinx-doc.orgttps://dont-be-afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-    your-changes/en/master/