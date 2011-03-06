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


Configuration and Testing
-------------------------
When running tests, you would want to avoid as much as possible setting up test
cases by creating a Pecan app on each instance. To avoid this, you need to
create a proper test configuration file and load it at setup time.

To do this, you need to know the absolute path for your configuration file and 
then call ``set_config`` with it. A typical ``setUp`` method would look like::

    def setUp(self):
        config_path = '/path/to/test_config.py'
        pecan.set_config(config_path)

        self.app = TestApp(
            make_app(
                config.app.root
                template_path   = config.app.template_path
            )
        )
        

As you can see, we are loading the configuration file into Pecan first and then
creating a Pecan application with it. Any interaction after ``setUp`` will be
exactly as if your application was really running via an HTTP server.


Using WebTest with a UnitTest
-----------------------------
Once you have a ``setUp`` method with your Pecan configuration loaded you have
a wealth of actions provided within the test class to interact with your Pecan
application::

 *  POST   => self.app.post
 *  GET    => self.app.get
 *  DELETE => self.app.delete
 *  PUT    => self.app.put

For example, if I wanted to assert that I can get the root of my application,
I would probably do something similar to this:

     response = self.app.get('/')
     assert response.status_int == 200

If you are expecting error responses from your application, you should make
sure that you pass the `expect_errors` flag and set it to True::

    response = self.app.get('/url/does/not/exist', expect_errors=True)
    assert response.status_int == 404

If you would like to dig in to more examples in how to test and verify more
actions, make sure you take a look at the 
`WebTest documentation <http://pythonpaste.org/webtest/>`_

