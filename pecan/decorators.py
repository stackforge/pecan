from inspect import getargspec
from util import _cfg

def when_for(controller):
    def when(method=None, **kw):
        def decorate(f):
            expose(**kw)(f)
            _cfg(f)['generic_handler'] = True
            controller._pecan['generic_handlers'][method.upper()] = f
            return f
        return decorate
    return when

def expose(template      = None, 
           content_type  = 'text/html', 
           schema        = None, 
           json_schema   = None, 
           error_handler = None,
           generic       = False):
    
    if template == 'json': content_type = 'application/json'
    def decorate(f):
        # flag the method as exposed
        f.exposed = True
        
        # set a "pecan" attribute, where we will store details
        cfg = _cfg(f)
        cfg['content_type'] = content_type
        cfg.setdefault('template', []).append(template)
        cfg.setdefault('content_types', {})[content_type] = template
        
        # handle generic controllers
        if generic:
            cfg['generic'] = True
            cfg['generic_handlers'] = dict(DEFAULT=f)
            f.when = when_for(f)
            
        # store the arguments for this controller method
        cfg['argspec'] = getargspec(f)
        
        # store the validator
        cfg['error_handler'] = error_handler
        if schema is not None: 
            cfg['schema'] = schema
            cfg['validate_json'] = False
        elif json_schema is not None: 
            cfg['schema'] = json_schema
            cfg['validate_json'] = True
        return f
    return decorate
    
def transactional(ignore_redirects=True):
    def deco(f):
        def wrap(*args, **kwargs):
            return f(*args, **kwargs)
        wrap.__transactional__ = True
        wrap.__transactional_ignore_redirects__ = ignore_redirects
        return wrap
    return deco
