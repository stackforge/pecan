import re
import warnings
from inspect import getmembers, ismethod

from webob import exc
import six

from .secure import handle_security, cross_boundary
from .util import iscontroller, getargspec, _cfg

__all__ = ['lookup_controller', 'find_object', 'route']
__observed_controllers__ = set()
__custom_routes__ = {}


def route(*args):
    """
    This function is used to define an explicit route for a path segment.

    You generally only want to use this in situations where your desired path
    segment is not a valid Python variable/function name.

    For example, if you wanted to be able to route to:

    /path/with-dashes/

    ...the following is invalid Python syntax::

        class Controller(object):

            with-dashes = SubController()

    ...so you would instead define the route explicitly::

        class Controller(object):
            pass

        pecan.route(Controller, 'with-dashes', SubController())
    """

    def _validate_route(route):
        if not isinstance(route, six.string_types):
            raise TypeError('%s must be a string' % route)

        if route in ('.', '..') or not re.match(
            '^[0-9a-zA-Z-_$\(\)\.~!,;:*+@=]+$', route
        ):
            raise ValueError(
                '%s must be a valid path segment.  Keep in mind '
                'that path segments should not contain path separators '
                '(e.g., /) ' % route
            )

    if len(args) == 2:
        # The handler in this situation is a @pecan.expose'd callable,
        # and is generally only used by the @expose() decorator itself.
        #
        # This sets a special attribute, `custom_route` on the callable, which
        # pecan's routing logic knows how to make use of (as a special case)
        route, handler = args
        if ismethod(handler):
            handler = handler.__func__
        if not iscontroller(handler):
            raise TypeError(
                '%s must be a callable decorated with @pecan.expose' % handler
            )
        obj, attr, value = handler, 'custom_route', route

        if handler.__name__ in ('_lookup', '_default', '_route'):
            raise ValueError(
                '%s is a special method in pecan and cannot be used in '
                'combination with custom path segments.' % handler.__name__
            )
    elif len(args) == 3:
        # This is really just a setattr on the parent controller (with some
        # additional validation for the path segment itself)
        _, route, handler = args
        obj, attr, value = args

        if hasattr(obj, attr):
            raise RuntimeError(
                (
                    "%(module)s.%(class)s already has an "
                    "existing attribute named \"%(route)s\"." % {
                        'module': obj.__module__,
                        'class': obj.__name__,
                        'route': attr
                    }
                ),
            )
    else:
        raise TypeError(
            'pecan.route should be called in the format '
            'route(ParentController, "path-segment", SubController())'
        )

    _validate_route(route)
    setattr(obj, attr, value)


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


def lookup_controller(obj, remainder, request=None):
    '''
    Traverses the requested url path and returns the appropriate controller
    object, including default routes.

    Handles common errors gracefully.
    '''
    if request is None:
        warnings.warn(
            (
                "The function signature for %s.lookup_controller is changing "
                "in the next version of pecan.\nPlease update to: "
                "`lookup_controller(self, obj, remainder, request)`." % (
                    __name__,
                )
            ),
            DeprecationWarning
        )

    notfound_handlers = []
    while True:
        try:
            obj, remainder = find_object(obj, remainder, notfound_handlers,
                                         request)
            handle_security(obj)
            return obj, remainder
        except (exc.HTTPNotFound, exc.HTTPMethodNotAllowed,
                PecanNotFound) as e:
            if isinstance(e, PecanNotFound):
                e = exc.HTTPNotFound()
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
                            remainder == [''] and
                            len(obj._pecan['argspec'].args) > 1
                        ):
                            raise e
                        obj_, remainder_ = result
                        return lookup_controller(obj_, remainder_, request)
            else:
                raise e


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


def find_object(obj, remainder, notfound_handlers, request):
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
            if getattr(obj, 'custom_route', None) is None:
                return obj, remainder

        _detect_custom_path_segments(obj)

        if remainder:
            custom_route = __custom_routes__.get((obj.__class__, remainder[0]))
            if custom_route:
                return getattr(obj, custom_route), remainder[1:]

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
            if len(getargspec(route).args) == 2:
                warnings.warn(
                    (
                        "The function signature for %s.%s._route is changing "
                        "in the next version of pecan.\nPlease update to: "
                        "`def _route(self, args, request)`." % (
                            obj.__class__.__module__,
                            obj.__class__.__name__
                        )
                    ),
                    DeprecationWarning
                )
                next_obj, next_remainder = route(remainder)
            else:
                next_obj, next_remainder = route(remainder, request)
            cross_boundary(route, next_obj)
            return next_obj, next_remainder

        if not remainder:
            raise PecanNotFound

        prev_remainder = remainder
        prev_obj = obj
        remainder = rest
        try:
            obj = getattr(obj, next_obj, None)
        except UnicodeEncodeError:
            obj = None

        # Last-ditch effort: if there's not a matching subcontroller, no
        # `_default`, no `_lookup`, and no `_route`, look to see if there's
        # an `index` that has a generic method defined for the current request
        # method.
        if not obj and not notfound_handlers and hasattr(prev_obj, 'index'):
            if request.method in _cfg(prev_obj.index).get('generic_handlers',
                                                          {}):
                return prev_obj.index, prev_remainder


def _detect_custom_path_segments(obj):
    # Detect custom controller routes (on the initial traversal)
    if obj.__class__.__module__ == '__builtin__':
        return

    attrs = set(dir(obj))

    if obj.__class__ not in __observed_controllers__:
        for key, val in getmembers(obj):
            if iscontroller(val) and isinstance(
                getattr(val, 'custom_route', None),
                six.string_types
            ):
                route = val.custom_route

                # Detect class attribute name conflicts
                for conflict in attrs.intersection(set((route,))):
                    raise RuntimeError(
                        (
                            "%(module)s.%(class)s.%(function)s has "
                            "a custom path segment, \"%(route)s\", "
                            "but %(module)s.%(class)s already has an "
                            "existing attribute named \"%(route)s\"." % {
                                'module': obj.__class__.__module__,
                                'class': obj.__class__.__name__,
                                'function': val.__name__,
                                'route': conflict
                            }
                        ),
                    )

                existing = __custom_routes__.get(
                    (obj.__class__, route)
                )
                if existing:
                    # Detect custom path conflicts between functions
                    raise RuntimeError(
                        (
                            "%(module)s.%(class)s.%(function)s and "
                            "%(module)s.%(class)s.%(other)s have a "
                            "conflicting custom path segment, "
                            "\"%(route)s\"." % {
                                'module': obj.__class__.__module__,
                                'class': obj.__class__.__name__,
                                'function': val.__name__,
                                'other': existing,
                                'route': route
                            }
                        ),
                    )

                __custom_routes__[
                    (obj.__class__, route)
                ] = key
        __observed_controllers__.add(obj.__class__)
