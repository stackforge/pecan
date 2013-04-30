import json

from webtest import TestApp
from six import b as b_

import pecan
from pecan.middleware.errordocument import ErrorDocumentMiddleware
from pecan.middleware.recursive import RecursiveMiddleware
from pecan.tests import PecanTestCase


def four_oh_four_app(environ, start_response):
    if environ['PATH_INFO'].startswith('/error'):
        code = environ['PATH_INFO'].split('/')[2]
        start_response("200 OK", [('Content-type', 'text/plain')])

        body = "Error: %s" % code
        if environ['QUERY_STRING']:
            body += "\nQS: %s" % environ['QUERY_STRING']
        return [b_(body)]
    start_response("404 Not Found", [('Content-type', 'text/plain')])
    return []


class TestErrorDocumentMiddleware(PecanTestCase):

    def setUp(self):
        super(TestErrorDocumentMiddleware, self).setUp()
        self.app = TestApp(RecursiveMiddleware(ErrorDocumentMiddleware(
            four_oh_four_app, {404: '/error/404'}
        )))

    def test_hit_error_page(self):
        r = self.app.get('/error/404')
        assert r.status_int == 200
        assert r.body == b_('Error: 404')

    def test_middleware_routes_to_404_message(self):
        r = self.app.get('/', expect_errors=True)
        assert r.status_int == 404
        assert r.body == b_('Error: 404')

    def test_error_endpoint_with_query_string(self):
        app = TestApp(RecursiveMiddleware(ErrorDocumentMiddleware(
            four_oh_four_app, {404: '/error/404?foo=bar'}
        )))
        r = app.get('/', expect_errors=True)
        assert r.status_int == 404
        assert r.body == b_('Error: 404\nQS: foo=bar')

    def test_error_with_recursion_loop(self):
        app = TestApp(RecursiveMiddleware(ErrorDocumentMiddleware(
            four_oh_four_app, {404: '/'}
        )))
        r = app.get('/', expect_errors=True)
        assert r.status_int == 404
        assert r.body == b_(
            'Error: 404 Not Found.  (Error page could not be fetched)'
        )

    def test_original_exception(self):

        class RootController(object):

            @pecan.expose()
            def index(self):
                if pecan.request.method != 'POST':
                    pecan.abort(405, 'You have to POST, dummy!')
                return 'Hello, World!'

            @pecan.expose('json')
            def error(self, status):
                return dict(
                    status=int(status),
                    reason=pecan.request.environ[
                        'pecan.original_exception'
                    ].detail
                )

        app = pecan.Pecan(RootController())
        app = RecursiveMiddleware(ErrorDocumentMiddleware(app, {
            405: '/error/405'
        }))
        app = TestApp(app)

        assert app.post('/').status_int == 200
        r = app.get('/', expect_errors=405)
        assert r.status_int == 405

        resp = json.loads(r.body.decode())
        assert resp['status'] == 405
        assert resp['reason'] == 'You have to POST, dummy!'
