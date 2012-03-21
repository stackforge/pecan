from unittest import TestCase
from webtest import TestApp

from pecan.middleware.errordocument import ErrorDocumentMiddleware
from pecan.middleware.recursive import RecursiveMiddleware


def four_oh_four_app(environ, start_response):
    if environ['PATH_INFO'].startswith('/error'):
        code = environ['PATH_INFO'].split('/')[2]
        start_response("200 OK", [('Content-type', 'text/plain')])

        body = "Error: %s" % code
        if environ['QUERY_STRING']:
            body += "\nQS: %s" % environ['QUERY_STRING']
        return [body]
    start_response("404 Not Found", [('Content-type', 'text/plain')])
    return []


class TestDebugMiddleware(TestCase):

    def setUp(self):
        self.app = TestApp(RecursiveMiddleware(ErrorDocumentMiddleware(
            four_oh_four_app, {404: '/error/404'}
        )))

    def test_hit_error_page(self):
        r = self.app.get('/error/404')
        assert r.status_int == 200
        assert r.body == 'Error: 404'

    def test_middleware_routes_to_404_message(self):
        r = self.app.get('/', expect_errors=True)
        assert r.status_int == 404
        assert r.body == 'Error: 404'

    def test_error_endpoint_with_query_string(self):
        app = TestApp(RecursiveMiddleware(ErrorDocumentMiddleware(
            four_oh_four_app, {404: '/error/404?foo=bar'}
        )))
        r = app.get('/', expect_errors=True)
        assert r.status_int == 404
        assert r.body == 'Error: 404\nQS: foo=bar'

    def test_error_with_recursion_loop(self):
        app = TestApp(RecursiveMiddleware(ErrorDocumentMiddleware(
            four_oh_four_app, {404: '/'}
        )))
        r = app.get('/', expect_errors=True)
        assert r.status_int == 404
        assert r.body == ('Error: 404 Not Found.  '
                          '(Error page could not be fetched)')
