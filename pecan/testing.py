from pecan import load_app
from webtest import TestApp


def load_test_app(config):
    """
    Used for functional tests where you need to test your
    literal application and its integration with the framework.

    :param config: Can be a dictionary containing configuration, or a string
                   which represents a (relative) configuration filename.

    returns a pecan.Pecan WSGI application wrapped in a webtest.TestApp
    instance.

    ::
        app = load_test_app('path/to/some/config.py')

        resp = app.get('/path/to/some/resource').status_int
        assert resp.status_int == 200

        resp = app.post('/path/to/some/resource', params={'param': 'value'})
        assert resp.status_int == 302
    """
    return TestApp(load_app(config))
