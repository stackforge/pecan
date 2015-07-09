from .core import (
    abort, override_template, Pecan, Request, Response, load_app,
    redirect, render, request, response
)
from .decorators import expose
from .hooks import RequestViewerHook

from .middleware.debug import DebugMiddleware
from .middleware.errordocument import ErrorDocumentMiddleware
from .middleware.recursive import RecursiveMiddleware
from .middleware.static import StaticFileMiddleware
from .routing import route

from .configuration import set_config, Config
from .configuration import _runtime_conf as conf
from . import middleware

try:
    from logging.config import dictConfig as load_logging_config
except ImportError:
    from logutils.dictconfig import dictConfig as load_logging_config  # noqa

import warnings


__all__ = [
    'make_app', 'load_app', 'Pecan', 'Request', 'Response', 'request',
    'response', 'override_template', 'expose', 'conf', 'set_config', 'render',
    'abort', 'redirect', 'route'
]


def make_app(root, **kw):
    '''
    Utility for creating the Pecan application object.  This function should
    generally be called from the ``setup_app`` function in your project's
    ``app.py`` file.

    :param root: A string representing a root controller object (e.g.,
                 "myapp.controller.root.RootController")
    :param static_root: The relative path to a directory containing static
                        files.  Serving static files is only enabled when
                        debug mode is set.
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
    :param logging: A dictionary used to configure logging.  This uses
                    ``logging.config.dictConfig``.

    All other keyword arguments are passed in to the Pecan app constructor.

    :returns: a ``Pecan`` object.
    '''
    # Pass logging configuration (if it exists) on to the Python logging module
    logging = kw.get('logging', {})
    debug = kw.get('debug', False)
    if logging:
        if debug:
            try:
                #
                # By default, Python 2.7+ silences DeprecationWarnings.
                # However, if conf.app.debug is True, we should probably ensure
                # that users see these types of warnings.
                #
                from logging import captureWarnings
                captureWarnings(True)
                warnings.simplefilter("default", DeprecationWarning)
            except ImportError:
                # No captureWarnings on Python 2.6, DeprecationWarnings are on
                pass

        if isinstance(logging, Config):
            logging = logging.to_dict()
        if 'version' not in logging:
            logging['version'] = 1
        load_logging_config(logging)

    # Instantiate the WSGI app by passing **kw onward
    app = Pecan(root, **kw)

    # Optionally wrap the app in another WSGI app
    wrap_app = kw.get('wrap_app', None)
    if wrap_app:
        app = wrap_app(app)

    # Configuration for serving custom error messages
    errors = kw.get('errors', getattr(conf.app, 'errors', {}))
    if errors:
        app = middleware.errordocument.ErrorDocumentMiddleware(app, errors)

    # Included for internal redirect support
    app = middleware.recursive.RecursiveMiddleware(app)

    # When in debug mode, load exception debugging middleware
    static_root = kw.get('static_root', None)
    if debug:
        debug_kwargs = getattr(conf, 'debug', {})
        debug_kwargs.setdefault('context_injectors', []).append(
            lambda environ: {
                'request': environ.get('pecan.locals', {}).get('request')
            }
        )
        app = DebugMiddleware(
            app,
            **debug_kwargs
        )

        # Support for serving static files (for development convenience)
        if static_root:
            app = middleware.static.StaticFileMiddleware(app, static_root)

    elif static_root:
        warnings.warn(
            "`static_root` is only used when `debug` is True, ignoring",
            RuntimeWarning
        )

    if hasattr(conf, 'requestviewer'):
        warnings.warn(''.join([
            "`pecan.conf.requestviewer` is deprecated.  To apply the ",
            "`RequestViewerHook` to your application, add it to ",
            "`pecan.conf.app.hooks` or manually in your project's `app.py` ",
            "file."]),
            DeprecationWarning
        )

    return app
