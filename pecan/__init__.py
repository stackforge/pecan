from paste.urlparser import StaticURLParser
from paste.cascade import Cascade

from pecan import Pecan, request, response, override_template
from decorators import expose

__all__ = [
    'make_app', 'Pecan', 'request', 'response', 'override_template', 'expose'
]


def make_app(root, static_root=None, **kw):        
    app = Pecan(root, **kw)
    if static_root:
        app = Cascade([StaticURLParser(static_root), app])
    return app