from paste.errordocument import make_errordocument
from paste.translogger import TransLogger

from core import (
    abort, override_template, Pecan, load_app, redirect, render,
    request, response
)
from recursive import RecursiveMiddleware
from decorators import expose
from hooks import RequestViewerHook
from static import SharedDataMiddleware
from debug import DebugMiddleware

from configuration import set_config
from configuration import _runtime_conf as conf


__all__ = [
    'make_app', 'load_app', 'Pecan', 'request', 'response',
    'override_template', 'expose', 'conf', 'set_config', 'render',
    'abort', 'ValidationException', 'redirect'
]


def make_app(root, static_root=None, debug=False, errorcfg={},
             wrap_app=None, logging=False, **kw):

    # A shortcut for the RequestViewerHook middleware.
    if hasattr(conf, 'requestviewer'):
        existing_hooks = kw.get('hooks', [])
        existing_hooks.append(RequestViewerHook(conf.requestviewer))
        kw['hooks'] = existing_hooks

    # Instantiate the WSGI app by passing **kw onward
    app = Pecan(root, **kw)

    # Optionally wrap the app in another WSGI app
    if wrap_app:
        app = wrap_app(app)

    # Included for internal redirect support
    app = RecursiveMiddleware(app)

    # When in debug mode, load our exception dumping middleware
    if debug:
        app = DebugMiddleware(app)

    # Configuration for serving custom error messages
    if hasattr(conf.app, 'errors'):
        app = make_errordocument(app, conf, **dict(conf.app.errors))

    # Support for serving static files (for development convenience)
    if static_root:
        app = SharedDataMiddleware(app, static_root)

    # Support for simple Apache-style logs
    if isinstance(logging, dict) or logging == True:
        app = TransLogger(app, **(isinstance(logging, dict) and logging or {}))

    return app
