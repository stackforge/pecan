from paste.urlparser import StaticURLParser
from paste.cascade import Cascade
from weberror.errormiddleware import ErrorMiddleware
from paste.recursive import RecursiveMiddleware

from pecan import Pecan, request, response, override_template, redirect, error_for
from decorators import expose

import configuration

__all__ = [
    'make_app', 'Pecan', 'request', 'response', 'override_template', 'expose', 'set_config'
]


def make_app(root, static_root=None, debug=False, errorcfg={}, **kw):
    app = Pecan(root, **kw)
    app = RecursiveMiddleware(app)
    app = ErrorMiddleware(app, debug=debug, **errorcfg)
    if static_root:
        app = Cascade([StaticURLParser(static_root), app])
    return app

def set_config(name):
    return configuration.import_runtime_conf(name)



