from inspect import getargspec
from util import _cfg

__all__ = [
    'expose', 'transactional', 'accept_noncanonical'
]


def when_for(controller):
    '''
    
    '''
    
    def when(method=None, **kw):
        def decorate(f):
            expose(**kw)(f)
            _cfg(f)['generic_handler'] = True
            controller._pecan['generic_handlers'][method.upper()] = f
            return f
        return decorate
    return when

def expose(template        = None, 
           content_type    = 'text/html', 
           schema          = None, 
           json_schema     = None, 
           variable_decode = False,
           error_handler   = None,
           htmlfill        = None,
           generic         = False):
    
    '''
    Decorator used to flag controller methods as being "exposed" for
    access via HTTP, and to configure that access.
    
    :param template: The path to a template, relative to the base template directory.
    :param content_type: The content-type to use for this template.
    :param schema: A ``formencode`` ``Schema`` object to use for validation.
    :param json_schema: A ``formencode`` ``Schema`` object to use for validation of JSON POST/PUT content.
    :param variable_decode: A boolean indicating if you want to use ``htmlfill``'s variable decode capability of transforming flat HTML form structures into nested ones.
    :param htmlfill: Indicates whether or not you want to use ``htmlfill`` for this controller.
    :param generic: A boolean which flags this as a "generic" controller, which uses generic functions based upon ``simplegeneric`` generic functions. Allows you to split a single controller into multiple paths based upon HTTP method.
    '''
    
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
        
        # store the schema
        cfg['error_handler'] = error_handler
        if schema is not None: 
            cfg['schema'] = schema
            cfg['validate_json'] = False
        elif json_schema is not None: 
            cfg['schema'] = json_schema
            cfg['validate_json'] = True
        
        # store the variable decode configuration
        if isinstance(variable_decode, dict) or variable_decode == True:
            _variable_decode = dict(dict_char='.', list_char='-')
            if isinstance(variable_decode, dict):
                _variable_decode.update(variable_decode)
            cfg['variable_decode'] = _variable_decode
        
        # store the htmlfill configuration
        if isinstance(htmlfill, dict) or htmlfill == True or schema is not None:
            _htmlfill = dict(auto_insert_errors=False)
            if isinstance(htmlfill, dict):
                _htmlfill.update(htmlfill)
            cfg['htmlfill'] = _htmlfill
        return f
    return decorate
    
def transactional(ignore_redirects=True):
    '''
    If utilizing the :mod:`pecan.hooks` ``TransactionHook``, allows you
    to flag a controller method as being wrapped in a transaction,
    regardless of HTTP method.
    
    :param ignore_redirects: Indicates if the hook should ignore redirects for this controller or not.
    '''
    
    def deco(f):
        _cfg(f)['transactional'] = True
        _cfg(f)['transactional_ignore_redirects'] = ignore_redirects
        return f
    return deco


def after_commit(action):
    '''
    If utilizing the :mod:`pecan.hooks` ``TransactionHook``, allows you
    to flag a controller method to perform a callable action after the
    commit is successfully issued.

    :param action: The callable to call after the commit is successfully issued.
    '''
    def deco(func):
        _cfg(func).setdefault('after_commit', []).append(action)
        return func
    return deco


def accept_noncanonical(func):
    '''
    Flags a controller method as accepting non-canoncial URLs.
    '''
    
    _cfg(func)['accept_noncanonical'] = True
    return func
