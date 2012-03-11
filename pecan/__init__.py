'''
'''

from paste.cascade import Cascade
from paste.errordocument import make_errordocument
from paste.recursive import RecursiveMiddleware
from paste.translogger import TransLogger
from paste.urlparser import StaticURLParser
from weberror.errormiddleware import ErrorMiddleware
from weberror.evalexception import EvalException

from core import (
    abort, override_template, Pecan, load_app, redirect, render,
    request, response, ValidationException
)
from decorators import expose
from hooks import RequestViewerHook
from templating import error_formatters

from configuration import set_config
from configuration import _runtime_conf as conf

__all__ = [
    'make_app', 'load_app', 'Pecan', 'request', 'response',
    'override_template', 'expose', 'conf', 'set_config', 'render',
    'abort', 'ValidationException', 'redirect'
]


def make_app(root, static_root=None, debug=False, errorcfg={},
             wrap_app=None, logging=False, **kw):
    '''

    '''
    if hasattr(conf, 'requestviewer'):
        existing_hooks = kw.get('hooks', [])
        existing_hooks.append(RequestViewerHook(conf.requestviewer))
        kw['hooks'] = existing_hooks

    app = Pecan(root, **kw)
    if wrap_app:
        app = wrap_app(app)
    app = RecursiveMiddleware(app)
    if debug:
        app = EvalException(
            app,
            templating_formatters=error_formatters,
            **errorcfg
        )
    else:
        app = ErrorMiddleware(app, **errorcfg)
    app = make_errordocument(app, conf, **dict(conf.app.errors))
    if static_root:
        app = Cascade([StaticURLParser(static_root), app])
    if isinstance(logging, dict) or logging == True:
        app = TransLogger(app, **(isinstance(logging, dict) and logging or {}))
    return app
