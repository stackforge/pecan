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
provides, you should already have this directory with a few tests.

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


Configuration and Testing
-------------------------
When you create a new project using the ``base`` project template, Pecan adds 
a reference to its ``py.test`` plugin to your project's ``setup.cfg`` file. 
This handles loading your Pecan configuration and setting up your app as 
defined by your project's ``app.py`` file.

If you've created your own project without using Pecan's template, you can 
load the plugin yourself by adding this to your ``setup.cfg`` file::

    [pytest]
    addopts = -p pecan.testing --with-config=./config.py

Alternatively, you can just pass those options to ``py.test`` directly.

By default, Pecan's testing plugin assumes you will be using the ``config.py`` 
configuration file to run your tests. To change which configuration file gets 
used once, run ``py.test`` with the `--with-config` option. To make the change 
permanent, modify that option in the `addopts` setting of your ``setup.cfg`` 
file.

Pecan's ``py.test`` plugin exposes two new variables in the ``py.test`` 
namespace: ``temp_dir`` and ``wsgi_app``.

``py.test.temp_dir`` is a temporary directory that you can use for your tests. 
It's created at startup and deleted after all tests have completed. When using 
locally distributed testing with py.test, this is guaranteed to be shared by 
each test process. This is useful if you need to create some initial resource 
(e.g., a database template) that is later copied by each test. If you're using 
remotely distributed testing, the directory won't be shared across nodes.

``py.test.wsgi_app`` is your Pecan app loaded and configured per your project's 
``app.py`` file. In your test's ``setUp`` method, you would wrap this with 
``TestApp``::

    from unittest import TestCase
    from webtest import TestApp

    import py.test

    class TestRootController(TestCase):
    
        def setUp(self):
            self.app = TestApp(py.test.wsgi_app)


Using WebTest with a UnitTest
-----------------------------
Once you have a ``setUp`` method with your ``TestApp`` created, you have a 
wealth of actions provided within the test class to interact with your Pecan
application::

 *  POST   => self.app.post
 *  GET    => self.app.get
 *  DELETE => self.app.delete
 *  PUT    => self.app.put

For example, if you want to assert that you can get to the root of your 
application, you could do something similar to this::

    response = self.app.get('/')
    assert response.status_int == 200

If you are expecting error responses from your application, make sure to pass 
`expect_errors=True`::

    response = self.app.get('/url/does/not/exist', expect_errors=True)
    assert response.status_int == 404

If you would like to dig in to more examples in how to test and verify more
actions, take a look at the 
`WebTest documentation <http://pythonpaste.org/webtest/>`_
