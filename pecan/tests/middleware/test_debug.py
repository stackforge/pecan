from wsgiref.util import setup_testing_defaults

from webtest import TestApp
from six import b as b_

from pecan.middleware.debug import DebugMiddleware
from pecan.tests import PecanTestCase


class StripPasteVar(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ.pop('paste.testing')
        return self.app(environ, start_response)


class TestDebugMiddleware(PecanTestCase):

    def setUp(self):
        super(TestDebugMiddleware, self).setUp()

        def conditional_error_app(environ, start_response):
            setup_testing_defaults(environ)
            if environ['PATH_INFO'] == '/error':
                assert 1 == 2
            start_response("200 OK", [('Content-type', 'text/plain')])
            return [b_('requested page returned')]
        self.app = TestApp(StripPasteVar(DebugMiddleware(
            conditional_error_app
        )))

    def test_middleware_passes_through_when_no_exception_raised(self):
        r = self.app.get('/')
        assert r.status_int == 200
        assert r.body == b_('requested page returned')

    def test_middleware_gives_stack_trace_on_errors(self):
        r = self.app.get('/error', expect_errors=True)
        assert r.status_int == 400
        assert b_('AssertionError') in r.body

    def test_middleware_complains_in_multi_process_environment(self):

        class MultiProcessApp(object):

            def __init__(self, app):
                self.app = app

            def __call__(self, environ, start_response):
                environ['wsgi.multiprocess'] = True
                return self.app(environ, start_response)

        def conditional_error_app(environ, start_response):
            start_response("200 OK", [('Content-type', 'text/plain')])
            return ['Hello, World!']

        app = TestApp(MultiProcessApp(DebugMiddleware(conditional_error_app)))
        self.assertRaises(
            RuntimeError,
            app.get,
            '/'
        )

    def test_middlware_allows_for_post_mortem_debugging(self):
        def patch_debugger(d):
            def _patched_debug_request():
                d.append(True)
            return _patched_debug_request

        debugger = []

        app = TestApp(StripPasteVar(DebugMiddleware(
            self.app,
            patch_debugger(debugger)
        )))

        r = app.get('/error', expect_errors=True)
        assert r.status_int == 400

        r = app.get('/__pecan_initiate_pdb__', expect_errors=True)
        assert len(debugger) > 0
