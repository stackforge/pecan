def expose(template=None, content_type='text/html'):
    if template == 'json': content_type = 'application/json'
    def decorate(f):
        f.exposed = True
        if not hasattr(f, 'pecan'): f.pecan = {}
        f.pecan['content_type'] = content_type
        f.pecan.setdefault('template', []).append(template)
        f.pecan.setdefault('content_types', {})[content_type] = template
        return f
    return decorate