from paste.urlparser import StaticURLParser
from paste.cascade import Cascade

from pecan import Pecan, request, override_template
from decorators import expose


def make_app(root, renderers        = None, 
                   default_renderer = None, 
                   template_path    = None, 
                   hooks            = None,
                   static_root      = None):
    
    kw = {}
    if renderers is not None: kw['renderers'] = renderers
    if default_renderer is not None: kw['default_renderer'] = default_renderer
    if template_path is not None: kw['template_path'] = template_path
    if hooks is not None: kw['hooks'] = hooks
    
    app = Pecan(root, **kw)
    
    if static_root:
        app = Cascade([StaticURLParser(static_root), app])
    
    return app