.. _testing:

Unit Testing 
=============
UnitTesting in Pecan is handled by ``WebTest``. It creates a fake Pecan
application that in turn allows you to make assertions on how those requests
and responses are being handled without starting an HTTP server at all.

Make sure you always have a separate configuration file for your tests. This
guide will assume that your test file is called ``test.py``.



