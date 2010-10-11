from inspect import getargspec

def expose(template=None, content_type='text/html'):
    if template == 'json': content_type = 'application/json'
    def decorate(f):
        # flag the method as exposed
        f.exposed = True
        
        # set a "pecan" attribute, where we will store details
        if not hasattr(f, 'pecan'): f.pecan = {}
        f.pecan['content_type'] = content_type
        f.pecan.setdefault('template', []).append(template)
        f.pecan.setdefault('content_types', {})[content_type] = template
        
        # store the arguments for this controller method
        f.pecan['argspec'] = getargspec(f)
        return f
    return decorate