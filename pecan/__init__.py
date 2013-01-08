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
    from .compat.dictconfig import dictConfig as load_logging_config  # noqa


__all__ = [
    'make_app', 'load_app', 'Pecan', 'request', 'response',
    'override_template', 'expose', 'conf', 'set_config', 'render',
    'abort', 'redirect'
]


def make_app(root, static_root=None, logging={}, debug=False,
             wrap_app=None, **kw):
    '''
    Utility for creating the Pecan application object.  This function should
    generally be called from the ``setup_app`` function in your project's
    ``app.py`` file.

    :param root: A string representing a root controller object (e.g.,
                 "myapp.controller.root.RootController")
    :param static_root: The relative path to a directory containing static
                        files.  Serving static files is only enabled when
                        debug mode is set.
    :param logging: A dictionary used to configure logging.  This uses
                    ``logging.config.dictConfig``.
    :param debug: A flag to enable debug mode.  This enables the debug
                  middleware and serving static files.
    :param wrap_app: A function or middleware class to wrap the Pecan app.
                     This must either be a wsgi middleware class or a
                     function that returns a wsgi application. This wrapper
                     is applied first before wrapping the application in
                     other middlewares such as Pecan's debug middleware.
                     This should be used if you want to use middleware to
                     perform authentication or intercept all requests before
                     they are routed to the root controller.

    All other keyword arguments are passed in to the Pecan app constructor.

    :returns: a ``Pecan`` object.
    '''
    # A shortcut for the RequestViewerHook middleware.
    if hasattr(conf, 'requestviewer'):
        existing_hooks = kw.get('hooks', [])
        existing_hooks.append(RequestViewerHook(conf.requestviewer))
        kw['hooks'] = existing_hooks

    # Pass logging configuration (if it exists) on to the Python logging module
    if logging:
        if isinstance(logging, Config):
            logging = logging.to_dict()
        if 'version' not in logging:
            logging['version'] = 1
        load_logging_config(logging)

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
