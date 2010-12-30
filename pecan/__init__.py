from paste.urlparser import StaticURLParser
from paste.cascade import Cascade
from weberror.errormiddleware import ErrorMiddleware
from paste.recursive import RecursiveMiddleware

from pecan import Pecan, request, response, override_template, abort, redirect, error_for
from decorators import expose

from configuration import set_config
from configuration import _runtime_conf as conf

__all__ = [
    'make_app', 'Pecan', 'request', 'response', 'override_template', 'expose', 'conf', 'set_config', 'use_config'
]

def make_app(root, static_root=None, debug=False, errorcfg={}, **kw):
    app = Pecan(root, **kw)
    app = RecursiveMiddleware(app)
    app = ErrorMiddleware(app, debug=debug, **errorcfg)
    if static_root:
        app = Cascade([StaticURLParser(static_root), app])
    return app
