from webtest import TestApp
from six import b as b_

from pecan.middleware.recursive import (RecursiveMiddleware,
                                        ForwardRequestException)
from pecan.tests import PecanTestCase


def simple_app(environ, start_response):
    start_response("200 OK", [('Content-type', 'text/plain')])
    return [b_('requested page returned')]


def error_docs_app(environ, start_response):
    if environ['PATH_INFO'] == '/not_found':
        start_response("404 Not found", [('Content-type', 'text/plain')])
        return [b_('Not found')]
    elif environ['PATH_INFO'] == '/error':
        start_response("200 OK", [('Content-type', 'text/plain')])
        return [b_('Page not found')]
    elif environ['PATH_INFO'] == '/recurse':
        raise ForwardRequestException('/recurse')
    else:
        return simple_app(environ, start_response)


class Middleware(object):
    def __init__(self, app, url='/error'):
        self.app = app
        self.url = url

    def __call__(self, environ, start_response):
        raise ForwardRequestException(self.url)


def forward(app):
    app = TestApp(RecursiveMiddleware(app))
    res = app.get('')

    assert res.headers['content-type'] == 'text/plain'
    assert res.status == '200 OK'
    assert 'requested page returned' in res
    res = app.get('/error')
    assert res.headers['content-type'] == 'text/plain'
    assert res.status == '200 OK'
    assert 'Page not found' in res
    res = app.get('/not_found')
    assert res.headers['content-type'] == 'text/plain'
    assert res.status == '200 OK'
    assert 'Page not found' in res
    try:
        res = app.get('/recurse')
    except AssertionError as e:
        if str(e).startswith('Forwarding loop detected'):
            pass
        else:
            raise AssertionError('Failed to detect forwarding loop')


class TestRecursiveMiddleware(PecanTestCase):

    def test_ForwardRequest_url(self):
        class TestForwardRequestMiddleware(Middleware):
            def __call__(self, environ, start_response):
                if environ['PATH_INFO'] != '/not_found':
                    return self.app(environ, start_response)
                raise ForwardRequestException(self.url)
        forward(TestForwardRequestMiddleware(error_docs_app))

    def test_ForwardRequest_url_with_params(self):
        class TestForwardRequestMiddleware(Middleware):
            def __call__(self, environ, start_response):
                if environ['PATH_INFO'] != '/not_found':
                    return self.app(environ, start_response)
                raise ForwardRequestException(self.url + '?q=1')
        forward(TestForwardRequestMiddleware(error_docs_app))

    def test_ForwardRequest_environ(self):
        class TestForwardRequestMiddleware(Middleware):
            def __call__(self, environ, start_response):
                if environ['PATH_INFO'] != '/not_found':
                    return self.app(environ, start_response)
                environ['PATH_INFO'] = self.url
                raise ForwardRequestException(environ=environ)
        forward(TestForwardRequestMiddleware(error_docs_app))

    def test_ForwardRequest_factory(self):

        class TestForwardRequestMiddleware(Middleware):
            def __call__(self, environ, start_response):
                if environ['PATH_INFO'] != '/not_found':
                    return self.app(environ, start_response)
                environ['PATH_INFO'] = self.url

                def factory(app):

                    class WSGIApp(object):

                        def __init__(self, app):
                            self.app = app

                        def __call__(self, e, start_response):
                            def keep_status_start_response(status, headers,
                                                           exc_info=None):
                                return start_response(
                                    '404 Not Found', headers, exc_info
                                )
                            return self.app(e, keep_status_start_response)

                    return WSGIApp(app)

                raise ForwardRequestException(factory=factory)

        app = TestForwardRequestMiddleware(error_docs_app)
        app = TestApp(RecursiveMiddleware(app))
        res = app.get('')
        assert res.headers['content-type'] == 'text/plain'
        assert res.status == '200 OK'
        assert 'requested page returned' in res
        res = app.get('/error')
        assert res.headers['content-type'] == 'text/plain'
        assert res.status == '200 OK'
        assert 'Page not found' in res
        res = app.get('/not_found', status=404)
        assert res.headers['content-type'] == 'text/plain'
        assert res.status == '404 Not Found'  # Different status
        assert 'Page not found' in res
        try:
            res = app.get('/recurse')
        except AssertionError as e:
            if str(e).startswith('Forwarding loop detected'):
                pass
            else:
                raise AssertionError('Failed to detect forwarding loop')

    def test_ForwardRequestException(self):
        class TestForwardRequestExceptionMiddleware(Middleware):
            def __call__(self, environ, start_response):
                if environ['PATH_INFO'] != '/not_found':
                    return self.app(environ, start_response)
                raise ForwardRequestException(path_info=self.url)
        forward(TestForwardRequestExceptionMiddleware(error_docs_app))
