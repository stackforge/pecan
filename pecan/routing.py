import warnings

from webob import exc

from .secure import handle_security, cross_boundary
from .util import iscontroller

__all__ = ['lookup_controller', 'find_object']


class PecanNotFound(Exception):
    pass


class NonCanonicalPath(Exception):
    '''
    Exception Raised when a non-canonical path is encountered when 'walking'
    the URI.  This is typically a ``POST`` request which requires a trailing
    slash.
    '''
    def __init__(self, controller, remainder):
        self.controller = controller
        self.remainder = remainder


def lookup_controller(obj, remainder):
    '''
    Traverses the requested url path and returns the appropriate controller
    object, including default routes.

    Handles common errors gracefully.
    '''
    notfound_handlers = []
    while True:
        try:
            obj, remainder = find_object(obj, remainder, notfound_handlers)
            handle_security(obj)
            return obj, remainder
        except (exc.HTTPNotFound, PecanNotFound):
            while notfound_handlers:
                name, obj, remainder = notfound_handlers.pop()
                if name == '_default':
                    # Notfound handler is, in fact, a controller, so stop
                    #   traversal
                    return obj, remainder
                else:
                    # Notfound handler is an internal redirect, so continue
                    #   traversal
                    result = handle_lookup_traversal(obj, remainder)
                    if result:
                        # If no arguments are passed to the _lookup, yet the
                        # argspec requires at least one, raise a 404
                        if (
                            remainder == ['']
                            and len(obj._pecan['argspec'].args) > 1
                        ):
                            raise exc.HTTPNotFound
                        return lookup_controller(*result)
            else:
                raise exc.HTTPNotFound


def handle_lookup_traversal(obj, args):
    try:
        result = obj(*args)
        if result:
            prev_obj = obj
            obj, remainder = result
            # crossing controller boundary
            cross_boundary(prev_obj, obj)
            return result
    except TypeError as te:
        msg = 'Got exception calling lookup(): %s (%s)'
        warnings.warn(
            msg % (te, te.args),
            RuntimeWarning
        )


def find_object(obj, remainder, notfound_handlers):
    '''
    'Walks' the url path in search of an action for which a controller is
    implemented and returns that controller object along with what's left
    of the remainder.
    '''
    prev_obj = None
    while True:
        if obj is None:
            raise PecanNotFound
        if iscontroller(obj):
            return obj, remainder

        # are we traversing to another controller
        cross_boundary(prev_obj, obj)
        try:
            next_obj, rest = remainder[0], remainder[1:]
            if next_obj == '':
                index = getattr(obj, 'index', None)
                if iscontroller(index):
                    return index, rest
        except IndexError:
            # the URL has hit an index method without a trailing slash
            index = getattr(obj, 'index', None)
            if iscontroller(index):
                raise NonCanonicalPath(index, [])

        default = getattr(obj, '_default', None)
        if iscontroller(default):
            notfound_handlers.append(('_default', default, remainder))

        lookup = getattr(obj, '_lookup', None)
        if iscontroller(lookup):
            notfound_handlers.append(('_lookup', lookup, remainder))

        route = getattr(obj, '_route', None)
        if iscontroller(route):
            next_obj, next_remainder = route(remainder)
            cross_boundary(route, next_obj)
            return next_obj, next_remainder

        if not remainder:
            raise PecanNotFound
        prev_obj = obj
        remainder = rest
        obj = getattr(obj, next_obj, None)
