Pecan
=====

A WSGI object-dispatching web framework, designed to be lean and fast with few
dependencies.

.. _travis: http://travis-ci.org/dreamhost/pecan
.. |travis| image:: https://secure.travis-ci.org/dreamhost/pecan.png

|travis|_

Installing
----------

::

    $ pip install pecan

...or, for the latest (unstable) tip::

    $ git clone https://github.com/dreamhost/pecan.git -b next
    $ cd pecan && python setup.py develop

Running Tests
-------------

::

    $ python setup.py test

...or, to run all tests across all supported environments::

    $ pip install tox && tox

Viewing Documentation
---------------------
`Available online <http://pecan.readthedocs.org>`_, or to build manually::

    $ cd docs && make html
    $ open docs/build/html/index.html

...or::

    $ cd docs && make man
    $ man docs/build/man/pecan.1

Contributing to Pecan
---------------------
To fix bugs or add features to Pecan, a GitHub account is required.

The general practice for contributing is to `fork Pecan
<http://help.github.com/fork-a-repo/>`_ and make changes in the ``next``
branch.  When you're finished, `send a pull request
<http://help.github.com/send-pull-requests/>`_ and the developers will review
your patch.

All contributions must:

    * Include accompanying tests.
    * Include narrative and API documentation if new features are added.
    * Be (generally) compliant with `PEP8
      <http://www.python.org/dev/peps/pep-0008/>`_.
    * Not break the test or build.  Before issuing a pull request, ``$ pip
      install tox && tox`` from your source to ensure that all tests still pass
      across multiple versions of Python.
    * Add your name to the (bottom of the) AUTHORS file.

Additional Help/Support
-----------------------
Most Pecan interaction is done via the #pecanpy channel on `FreeNode
<http://freenode.net/>`_ IRC.
