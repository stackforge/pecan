from webob import exc


def lookup_controller(obj, url_path):
    remainder = url_path
    notfound_handlers = []
    while True:
        try:
            obj, remainder = find_object(obj, remainder, notfound_handlers)
            return obj, remainder
        except exc.HTTPNotFound:
            while notfound_handlers:
                name, obj, remainder = notfound_handlers.pop()
                if name == '_default':
                    # Notfound handler is, in fact, a controller, so stop
                    #   traversal
                    return obj, remainder
                else:
                    # Notfound handler is an internal redirect, so continue
                    #   traversal
                    try:
                        result = obj(*remainder)
                        if result:
                            obj, remainder = result
                            break
                    except TypeError, te:
                        print 'Got exception calling lookup(): %s (%s)' % (te, te.args)
            else:
                raise exc.HTTPNotFound


def find_object(obj, remainder, notfound_handlers):
    while True:
        if obj is None: raise exc.HTTPNotFound
        if iscontroller(obj): return obj, remainder
        
        if remainder and remainder[0] == '':
            index = getattr(obj, 'index', None)
            if iscontroller(index): return index, remainder[1:]
        elif not remainder:
            index = getattr(obj, 'index', None)
            if iscontroller(index):
                return index, remainder[1:] # TODO: why did I have to do this instead?
                #raise exc.HTTPFound(add_slash=True)

        default = getattr(obj, '_default', None)
        if iscontroller(default):
            notfound_handlers.append(('_default', default, remainder))

        lookup = getattr(obj, '_lookup', None)
        if iscontroller(lookup):
            notfound_handlers.append(('_lookup', lookup, remainder))
        
        route = getattr(obj, '_route', None)
        if iscontroller(route):
            return route(remainder)
        
        if not remainder: raise exc.HTTPNotFound
        next, remainder = remainder[0], remainder[1:]
        obj = getattr(obj, next, None)


def iscontroller(obj):
    return getattr(obj, 'exposed', False)