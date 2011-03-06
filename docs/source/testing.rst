.. _testing:

Unit Testing 
=============
UnitTesting in Pecan is handled by ``WebTest``. It creates a fake Pecan
application that in turn allows you to make assertions on how those requests
and responses are being handled without starting an HTTP server at all.


Tools
-----
Pecan recommends using ``py.test``. It is actually a project requirement when
you install Pecan so you should already have it installed. 


Structure 
---------
This guide assumes that you have all your tests in a ``tests`` directory. If
you have created a project from the ``base`` project template that Pecan
provides you should already have this directory with a few tests.

The template project uses UnitTest-type tests and some of those tests use
WebTest. We will describe how they work in the next section.

This is how running those tests with ``py.test`` would look like::

    $ py.test
    ============== test session starts =============
    platform darwin -- Python 2.6.1 -- pytest-2.0.1
    collected 11 items 

    ./tests/test_config.py .........
    ./tests/test_root.py ..

    ========== 11 passed in 0.30 seconds ===========





