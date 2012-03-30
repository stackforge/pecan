from webob import exc

from secure import handle_security, cross_boundary
from util import iscontroller

__all__ = ['lookup_controller', 'find_object']


class NonCanonicalPath(Exception):
    '''
    Exception Raised when a non-canonical path is encountered when 'walking'
    the URI.  This is typically a ``POST`` request which requires a trailing
    slash.
    '''
    def __init__(self, controller, remainder):
        self.controller = controller
        self.remainder = remainder


def lookup_controller(obj, url_path):
    '''
    Traverses the requested url path and returns the appropriate controller
    object, including default routes.

    Handles common errors gracefully.
    '''
    remainder = url_path
    notfound_handlers = []

    while True:
        try:
            obj, remainder = find_object(obj, remainder, notfound_handlers)
            handle_security(obj)
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
                            prev_obj = obj
                            obj, remainder = result
                            # crossing controller boundary
                            cross_boundary(prev_obj, obj)
                            break
                    except TypeError, te:
                        import warnings
                        msg = 'Got exception calling lookup(): %s (%s)'
                        warnings.warn(
                            msg % (te, te.args),
                            RuntimeWarning
                        )
            else:
                raise exc.HTTPNotFound


def find_object(obj, remainder, notfound_handlers):
    '''
    'Walks' the url path in search of an action for which a controller is
    implemented and returns that controller object along with what's left
    of the remainder.
    '''
    prev_obj = None
    while True:
        if obj is None:
            raise exc.HTTPNotFound
        if iscontroller(obj):
            return obj, remainder

        # are we traversing to another controller
        cross_boundary(prev_obj, obj)

        if remainder and remainder[0] == '':
            index = getattr(obj, 'index', None)
            if iscontroller(index):
                return index, remainder[1:]
        elif not remainder:
            # the URL has hit an index method without a trailing slash
            index = getattr(obj, 'index', None)
            if iscontroller(index):
                raise NonCanonicalPath(index, remainder[1:])
        default = getattr(obj, '_default', None)
        if iscontroller(default):
            notfound_handlers.append(('_default', default, remainder))

        lookup = getattr(obj, '_lookup', None)
        if iscontroller(lookup):
            notfound_handlers.append(('_lookup', lookup, remainder))

        route = getattr(obj, '_route', None)
        if iscontroller(route):
            next, next_remainder = route(remainder)
            cross_boundary(route, next)
            return next, next_remainder

        if not remainder:
            raise exc.HTTPNotFound
        next, remainder = remainder[0], remainder[1:]
        prev_obj = obj
        obj = getattr(obj, next, None)
