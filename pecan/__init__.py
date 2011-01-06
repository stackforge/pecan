from paste.urlparser import StaticURLParser
from paste.cascade import Cascade
from weberror.errormiddleware import ErrorMiddleware
from weberror.evalexception import EvalException
from paste.recursive import RecursiveMiddleware

from core import Pecan, context, request, response, override_template, abort, redirect, error_for
from decorators import expose

from configuration import set_config
from configuration import _runtime_conf as conf

__all__ = [
    'make_app', 'Pecan', 'request', 'response', 'override_template', 'expose', 'conf', 'set_config', 'use_config'
]

def make_app(root, static_root=None, debug=False, errorcfg={}, wrap_app=None, **kw):
    app = Pecan(root, **kw)
    if wrap_app:
        app = wrap_app(app)
    app = RecursiveMiddleware(app)
    if debug:
        app = EvalException(app, **errorcfg)
    else:
        app = ErrorMiddleware(app, **errorcfg)
    if static_root:
        app = Cascade([StaticURLParser(static_root), app])
    return app
