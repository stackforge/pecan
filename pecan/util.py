def iscontroller(obj):
    return getattr(obj, 'exposed', False)

def _cfg(f):
    if not hasattr(f, '_pecan'): f._pecan = {}
    return f._pecan
