.. _testing:

Testing Pecan Applications
==========================
Tests can live anywhere in your Pecan project as long as the test runner can
discover them. Traditionally, they exist in a package named ``myapp.tests``.

The suggested mechanism for unit and integration testing of a Pecan application
is the :mod:`unittest` module.

Test Discovery and Other Tools
------------------------------

Tests for a Pecan project can be invoked as simply as ``python setup.py test``,
though it's possible to run your tests with different discovery and automation
tools.  In particular, Pecan projects are known to work well with
`nose <http://pypi.python.org/pypi/nose/1.1.2>`_, `pytest
<http://pytest.org>`_,
and `tox <http://pypi.python.org/pypi/tox>`_.

Writing Functional Tests with WebTest
-------------------------------------
A **unit test** typically relies on "mock" or "fake" objects to give the code
under test enough context to run.  In this way, only an individual unit of
source code is tested.

A healthy suite of tests combines **unit tests** with **functional tests**.  In
the context of a Pecan application, functional tests can be written with the
help of the :mod:`webtest` library.  In this way, it is possible to write tests
that verify the behavior of an HTTP request life cycle from the controller
routing down to the HTTP response.  The following is an example that is
similar to the one included with Pecan's quickstart project.

::

    # myapp/myapp/tests/__init__.py

    import os
    from unittest import TestCase
    from pecan import set_config
    from pecan.testing import load_test_app

    class FunctionalTest(TestCase):
        """
        Used for functional tests where you need to test your
        literal application and its integration with the framework.
        """
        
        def setUp(self):
            self.app = load_test_app(os.path.join(
                os.path.dirname(__file__),
                'config.py'
            ))

        def tearDown(self):
            set_config({}, overwrite=True)

The testing utility included with Pecan, :func:`pecan.testing.load_test_app`, can
be passed a file path representing a Pecan configuration file, and will return
an instance of the application, wrapped in a :class:`~webtest.app.TestApp`
environment.

From here, it's possible to extend the :class:`FunctionalTest` base class and write
tests that issue simulated HTTP requests.

::

    class TestIndex(FunctionalTest):

        def test_index(self):
            resp = self.app.get('/')
            assert resp.status_int == 200
            assert 'Hello, World' in resp.body

.. seealso::

  See the :mod:`webtest` documentation
  for further information about the methods available to a
  :class:`~webtest.app.TestApp` instance.

Special Testing Variables
-------------------------

Sometimes it's not enough to make assertions about the response body of certain
requests.  To aid in inspection, Pecan applications provide a special set of
"testing variables" to any :class:`~webtest.response.TestResponse` object.

Let's suppose that your Pecan applicaton had some controller which took a 
``name`` as an optional argument in the URL.

::

    # myapp/myapp/controllers/root.py
    from pecan import expose

    class RootController(object):

        @expose('index.html')
        def index(self, name='Joe'):
            """A request to / will access this controller"""
            return dict(name=name)

and rendered that name in it's template (and thus, the response body).

::

    # myapp/myapp/templates/index.html
    Hello, ${name}!

A functional test for this controller might look something like

::

    class TestIndex(FunctionalTest):

        def test_index(self):
            resp = self.app.get('/')
            assert resp.status_int == 200
            assert 'Hello, Joe!' in resp.body

In addition to :attr:`webtest.TestResponse.body`, Pecan also provides
:attr:`webtest.TestResponse.namespace`, which represents the template namespace
returned from the controller, and :attr:`webtest.TestResponse.template_name`, which
contains the name of the template used.

::

    class TestIndex(FunctionalTest):

        def test_index(self):
            resp = self.app.get('/')
            assert resp.status_int == 200
            assert resp.namespace == {'name': 'Joe'}
            assert resp.template_name == 'index.html'

In this way, it's possible to test the return value and rendered template of
individual controllers.
