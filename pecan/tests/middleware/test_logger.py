from cStringIO import StringIO
from unittest import TestCase
from webtest import TestApp

from pecan.middleware.logger import TransLogger


def simple_app(environ, start_response):
    start_response("200 OK", [('Content-type', 'text/plain')])
    return ['Hello, World']


class FakeLogger(object):

    def __init__(self):
        self.b = StringIO()

    def log(self, level, msg):
        self.b.write(msg)

    def getvalue(self):
        return self.b.getvalue()


class TestDebugMiddleware(TestCase):

    def setUp(self):
        self.logger = FakeLogger()

    def test_simple_log(self):
        app = TestApp(TransLogger(simple_app, logger=self.logger))
        r = app.get('/')
        assert r.status_int == 200
        assert r.body == 'Hello, World'
        assert '"GET / HTTP/1.0" 200 - "-" "-"' in self.logger.getvalue()

    def test_log_format(self):
        app = TestApp(TransLogger(simple_app, logger=self.logger, format='X'))
        r = app.get('/')
        assert r.status_int == 200
        assert r.body == 'Hello, World'
        assert self.logger.getvalue() == 'X'

    def test_log_query_string(self):
        app = TestApp(TransLogger(simple_app, logger=self.logger))
        r = app.get('/?foo=1')
        assert r.status_int == 200
        assert r.body == 'Hello, World'
        assert '"GET /?foo=1 HTTP/1.0" 200 - "-" "-"' in self.logger.getvalue()
