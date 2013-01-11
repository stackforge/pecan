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
    $ cd pecan && python setup.py install

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

Additional Help/Support
-----------------------
Most Pecan interaction is done via the #pecanpy channel on `FreeNode
<http://freenode.net/>`_ IRC.
