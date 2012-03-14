# (c) 2005 Ian Bicking and contributors; written for Paste
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

"""
Middleware to make internal requests and forward requests internally.

Raise ``ForwardRequestException(new_path_info)`` to do a forward
(aborting the current request).
"""

from cStringIO import StringIO

import warnings

__all__ = ['RecursiveMiddleware']


class RecursionLoop(AssertionError):
    # Subclasses AssertionError for legacy reasons
    """Raised when a recursion enters into a loop"""


class CheckForRecursionMiddleware(object):
    def __init__(self, app, env):
        self.app = app
        self.env = env

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if path_info in self.env.get(
            'pecan.recursive.old_path_info', []):
            raise RecursionLoop(
                "Forwarding loop detected; %r visited twice (internal "
                "redirect path: %s)"
                % (path_info, self.env['pecan.recursive.old_path_info']))
        old_path_info = self.env.setdefault(
            'pecan.recursive.old_path_info', []
        )
        old_path_info.append(self.env.get('PATH_INFO', ''))
        return self.app(environ, start_response)


class RecursiveMiddleware(object):

    """
    A WSGI middleware that allows for recursive and forwarded calls.
    All these calls go to the same 'application', but presumably that
    application acts differently with different URLs.  The forwarded
    URLs must be relative to this container.

    Interface is entirely through the ``pecan.recursive.forward``
    environmental key.
    """

    def __init__(self, application, global_conf=None):
        self.application = application

    def __call__(self, environ, start_response):
        environ['pecan.recursive.forward'] = Forwarder(
            self.application,
            environ,
            start_response)
        my_script_name = environ.get('SCRIPT_NAME', '')
        environ['pecan.recursive.script_name'] = my_script_name
        try:
            return self.application(environ, start_response)
        except ForwardRequestException, e:
            middleware = CheckForRecursionMiddleware(
                e.factory(self), environ)
            return middleware(environ, start_response)


class ForwardRequestException(Exception):
    """
    Used to signal that a request should be forwarded to a different location.

    ``url``
        The URL to forward to starting with a ``/`` and relative to
        ``RecursiveMiddleware``. URL fragments can also contain query strings
        so ``/error?code=404`` would be a valid URL fragment.

    ``environ``
        An altertative WSGI environment dictionary to use for the forwarded
        request. If specified is used *instead* of the ``url_fragment``

    ``factory``
        If specifed ``factory`` is used instead of ``url`` or ``environ``.
        ``factory`` is a callable that takes a WSGI application object
        as the first argument and returns an initialised WSGI middleware
        which can alter the forwarded response.

    Basic usage (must have ``RecursiveMiddleware`` present) :

    .. code-block:: python

        from pecan.recursive import ForwardRequestException
        def app(environ, start_response):
            if environ['PATH_INFO'] == '/hello':
                start_response("200 OK", [('Content-type', 'text/plain')])
                return ['Hello World!']
            elif environ['PATH_INFO'] == '/error':
                start_response("404 Not Found",
                    [('Content-type', 'text/plain')]
                )
                return ['Page not found']
            else:
                raise ForwardRequestException('/error')

        from pecan.recursive import RecursiveMiddleware
        app = RecursiveMiddleware(app)

    If you ran this application and visited ``/hello`` you would get a
    ``Hello World!`` message. If you ran the application and visited
    ``/not_found`` a ``ForwardRequestException`` would be raised and the caught
    by the ``RecursiveMiddleware``. The ``RecursiveMiddleware`` would then
    return the headers and response from the ``/error`` URL but would display
    a ``404 Not found`` status message.

    You could also specify an ``environ`` dictionary instead of a url. Using
    the same example as before:

    .. code-block:: python

        def app(environ, start_response):
            ... same as previous example ...
            else:
                new_environ = environ.copy()
                new_environ['PATH_INFO'] = '/error'
                raise ForwardRequestException(environ=new_environ)
    """

    def __init__(self, url=None, environ={}, factory=None, path_info=None):
        # Check no incompatible options have been chosen
        if factory and url:
            raise TypeError(  # pragma: no cover
                'You cannot specify factory and a url in '
                'ForwardRequestException')
        elif factory and environ:
            raise TypeError(  # pragma: no cover
                'You cannot specify factory and environ in '
                'ForwardRequestException')
        if url and environ:
            raise TypeError(  # pragma: no cover
                'You cannot specify environ and url in '
                'ForwardRequestException')

        # set the path_info or warn about its use.
        if path_info:
            if not url:
                warnings.warn(
                    ("ForwardRequestException(path_info=...) "
                     "has been deprecated; please "
                     "use ForwardRequestException(url=...)"),
                    DeprecationWarning, 2)
            else:
                raise TypeError(('You cannot use url and path_info '
                    'in ForwardRequestException'))  # pragma: no cover
            self.path_info = path_info

        # If the url can be treated as a path_info do that
        if url and not '?' in str(url):
            self.path_info = url

        # Base middleware
        class ForwardRequestExceptionMiddleware(object):
            def __init__(self, app):
                self.app = app

        # Otherwise construct the appropriate middleware factory
        if hasattr(self, 'path_info'):
            p = self.path_info

            def factory_pi(app):
                class PathInfoForward(ForwardRequestExceptionMiddleware):
                    def __call__(self, environ, start_response):
                        environ['PATH_INFO'] = p
                        return self.app(environ, start_response)
                return PathInfoForward(app)

            self.factory = factory_pi
        elif url:
            def factory_url(app):
                class URLForward(ForwardRequestExceptionMiddleware):
                    def __call__(self, environ, start_response):
                        environ['PATH_INFO'] = url.split('?')[0]
                        environ['QUERY_STRING'] = url.split('?')[1]
                        return self.app(environ, start_response)
                return URLForward(app)

            self.factory = factory_url
        elif environ:
            def factory_env(app):
                class EnvironForward(ForwardRequestExceptionMiddleware):
                    def __call__(self, environ_, start_response):
                        return self.app(environ, start_response)
                return EnvironForward(app)

            self.factory = factory_env
        else:
            self.factory = factory


class Recursive(object):

    def __init__(self, application, environ, start_response):
        self.application = application
        self.original_environ = environ.copy()
        self.previous_environ = environ
        self.start_response = start_response

    def __call__(self, path, extra_environ=None):
        """
        `extra_environ` is an optional dictionary that is also added
        to the forwarded request.  E.g., ``{'HTTP_HOST': 'new.host'}``
        could be used to forward to a different virtual host.
        """
        environ = self.original_environ.copy()
        if extra_environ:
            environ.update(extra_environ)
        environ['pecan.recursive.previous_environ'] = self.previous_environ
        base_path = self.original_environ.get('SCRIPT_NAME')
        if path.startswith('/'):
            assert path.startswith(base_path), (
                "You can only forward requests to resources under the "
                "path %r (not %r)" % (base_path, path))
            path = path[len(base_path) + 1:]
        assert not path.startswith('/')
        path_info = '/' + path
        environ['PATH_INFO'] = path_info
        environ['REQUEST_METHOD'] = 'GET'
        environ['CONTENT_LENGTH'] = '0'
        environ['CONTENT_TYPE'] = ''
        environ['wsgi.input'] = StringIO('')
        return self.activate(environ)

    def activate(self, environ):
        raise NotImplementedError  # pragma: no cover

    def __repr__(self):
        return '<%s.%s from %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.original_environ.get('SCRIPT_NAME') or '/')


class Forwarder(Recursive):

    """
    The forwarder will try to restart the request, except with
    the new `path` (replacing ``PATH_INFO`` in the request).

    It must not be called after and headers have been returned.
    It returns an iterator that must be returned back up the call
    stack, so it must be used like:

    .. code-block:: python

        return environ['pecan.recursive.forward'](path)

    Meaningful transformations cannot be done, since headers are
    sent directly to the server and cannot be inspected or
    rewritten.
    """

    def activate(self, environ):
        warnings.warn(
            "recursive.Forwarder has been deprecated; please use "
            "ForwardRequestException",
            DeprecationWarning, 2)
        return self.application(environ, self.start_response)
