from core import (
    abort, override_template, Pecan, load_app, redirect, render,
    request, response
)
from decorators import expose
from hooks import RequestViewerHook
from middleware.debug import DebugMiddleware
from middleware.errordocument import ErrorDocumentMiddleware
from middleware.recursive import RecursiveMiddleware
from middleware.static import StaticFileMiddleware

from configuration import set_config, Config
from configuration import _runtime_conf as conf

try:
    from logging.config import dictConfig as load_logging_config
except ImportError:
    from .compat.dictconfig import dictConfig as load_logging_config


__all__ = [
    'make_app', 'load_app', 'Pecan', 'request', 'response',
    'override_template', 'expose', 'conf', 'set_config', 'render',
    'abort', 'redirect'
]


def make_app(root, static_root=None, logging={}, debug=False,
             wrap_app=None, **kw):

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

    # Configuration for serving custom error messages
    if hasattr(conf.app, 'errors'):
        app = ErrorDocumentMiddleware(app, conf.app.errors)

    # Included for internal redirect support
    app = RecursiveMiddleware(app)

    # Pass logging configuration (if it exists) on to the Python logging module
    if logging:
        if isinstance(logging, Config):
            logging = logging.to_dict()
        if 'version' not in logging:
            logging['version'] = 1
        load_logging_config(logging)

    # When in debug mode, load our exception dumping middleware
    if debug:
        app = DebugMiddleware(app)

        # Support for serving static files (for development convenience)
        if static_root:
            app = StaticFileMiddleware(app, static_root)
    elif static_root:
        from warnings import warn
        warn(
            "`static_root` is only used when `debug` is True, ignoring",
            RuntimeWarning
        )

    return app
