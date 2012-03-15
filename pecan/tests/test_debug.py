from unittest import TestCase
from webtest import TestApp

from pecan.debug import DebugMiddleware


class TestDebugMiddleware(TestCase):

    def setUp(self):
        def conditional_error_app(environ, start_response):
            if environ['PATH_INFO'] == '/error':
                assert 1 == 2
            start_response("200 OK", [('Content-type', 'text/plain')])
            return ['requested page returned']
        self.app = TestApp(DebugMiddleware(conditional_error_app))

    def test_middleware_passes_through_when_no_exception_raised(self):
        r = self.app.get('/')
        assert r.status_int == 200
        assert r.body == 'requested page returned'

    def test_middleware_gives_stack_trace_on_errors(self):
        r = self.app.get('/error', expect_errors=True)
        assert r.status_int == 400
        assert 'AssertionError' in r.body
