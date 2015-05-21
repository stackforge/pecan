from inspect import ismethod, getmembers
import warnings

from webob import exc
import six

from .core import abort
from .decorators import expose
from .routing import lookup_controller, handle_lookup_traversal
from .util import iscontroller, getargspec


class RestController(object):
    '''
    A base class for ``REST`` based controllers. Inherit from this class
    to implement a REST controller.

    ``RestController`` implements a set of routing functions which override
    the default pecan routing with behavior consistent with RESTful routing.
    This functionality covers navigation to the requested resource
    controllers, and the appropriate handling of both the common (``GET``,
    ``POST``, ``PUT``, ``DELETE``) as well as custom-defined REST action
    methods.

    For more on developing **RESTful** web applications with Pecan, see
    :ref:`rest`.
    '''
    _custom_actions = {}

    def __new__(cls, *args, **kwargs):
        """
        RestController does not support the `route` argument to
        :func:`~pecan.decorators.expose`

        Implement this with __new__ rather than a metaclass, because it's very
        common for pecan users to mixin RestController (with other bases that
        have their own metaclasses).
        """
        for name, value in getmembers(cls):
            if iscontroller(value) and getattr(value, 'custom_route', None):
                raise ValueError(
                    'Path segments cannot be used in combination with '
                    'pecan.rest.RestController.  Remove the `route` argument '
                    'to @pecan.expose on %s.%s.%s' % (
                        cls.__module__, cls.__name__, value.__name__
                    )
                )

        # object.__new__ will error if called with extra arguments, and either
        # __new__ is overridden or __init__ is not overridden;
        # https://hg.python.org/cpython/file/78d36d54391c/Objects/typeobject.c#l3034
        # In PY3, this is actually a TypeError (in PY2, it just raises
        # a DeprecationWarning)
        new = super(RestController, cls).__new__
        if new is object.__new__:
            return new(cls)
        return new(cls, *args, **kwargs)

    def _get_args_for_controller(self, controller):
        """
        Retrieve the arguments we actually care about.  For Pecan applications
        that utilize thread locals, we should truncate the first argument,
        `self`.  For applications that explicitly pass request/response
        references as the first controller arguments, we should truncate the
        first three arguments, `self, req, resp`.
        """
        argspec = getargspec(controller)
        from pecan import request
        try:
            request.path
        except AttributeError:
            return argspec.args[3:]
        return argspec.args[1:]

    def _handle_bad_rest_arguments(self, controller, remainder, request):
        """
        Ensure that the argspec for a discovered controller actually matched
        the positional arguments in the request path.  If not, raise
        a webob.exc.HTTPBadRequest.
        """
        argspec = self._get_args_for_controller(controller)
        fixed_args = len(argspec) - len(
            request.pecan.get('routing_args', [])
        )
        if len(remainder) < fixed_args:
            # For controllers that are missing intermediate IDs
            # (e.g., /authors/books vs /authors/1/books), return a 404 for an
            # invalid path.
            abort(404)

    def _lookup_child(self, remainder):
        """
        Lookup a child controller with a named path (handling Unicode paths
        properly for Python 2).
        """
        try:
            controller = getattr(self, remainder, None)
        except UnicodeEncodeError:
            return None
        return controller

    @expose()
    def _route(self, args, request=None):
        '''
        Routes a request to the appropriate controller and returns its result.

        Performs a bit of validation - refuses to route delete and put actions
        via a GET request).
        '''
        if request is None:
            from pecan import request
        # convention uses "_method" to handle browser-unsupported methods
        method = request.params.get('_method', request.method).lower()

        # make sure DELETE/PUT requests don't use GET
        if request.method == 'GET' and method in ('delete', 'put'):
            abort(405)

        # check for nested controllers
        result = self._find_sub_controllers(args, request)
        if result:
            return result

        # handle the request
        handler = getattr(
            self,
            '_handle_%s' % method,
            self._handle_unknown_method
        )

        try:
            if len(getargspec(handler).args) == 3:
                result = handler(method, args)
            else:
                result = handler(method, args, request)

            #
            # If the signature of the handler does not match the number
            # of remaining positional arguments, attempt to handle
            # a _lookup method (if it exists)
            #
            argspec = self._get_args_for_controller(result[0])
            num_args = len(argspec)
            if num_args < len(args):
                _lookup_result = self._handle_lookup(args, request)
                if _lookup_result:
                    return _lookup_result
        except (exc.HTTPClientError, exc.HTTPNotFound,
                exc.HTTPMethodNotAllowed) as e:
            #
            # If the matching handler results in a 400, 404, or 405, attempt to
            # handle a _lookup method (if it exists)
            #
            _lookup_result = self._handle_lookup(args, request)
            if _lookup_result:
                return _lookup_result

            # Build a correct Allow: header
            if isinstance(e, exc.HTTPMethodNotAllowed):

                def method_iter():
                    for func in ('get', 'get_one', 'get_all', 'new', 'edit',
                                 'get_delete'):
                        if self._find_controller(func):
                            yield 'GET'
                            break
                    for method in ('HEAD', 'POST', 'PUT', 'DELETE', 'TRACE',
                                   'PATCH'):
                        func = method.lower()
                        if self._find_controller(func):
                            yield method

                e.allow = sorted(method_iter())

            raise

        # return the result
        return result

    def _handle_lookup(self, args, request=None):
        if request is None:
            self._raise_method_deprecation_warning(self.handle_lookup)

        # filter empty strings from the arg list
        args = list(six.moves.filter(bool, args))

        # check for lookup controllers
        lookup = getattr(self, '_lookup', None)
        if args and iscontroller(lookup):
            result = handle_lookup_traversal(lookup, args)
            if result:
                obj, remainder = result
                return lookup_controller(obj, remainder, request)

    def _find_controller(self, *args):
        '''
        Returns the appropriate controller for routing a custom action.
        '''
        for name in args:
            obj = self._lookup_child(name)
            if obj and iscontroller(obj):
                return obj
        return None

    def _find_sub_controllers(self, remainder, request):
        '''
        Identifies the correct controller to route to by analyzing the
        request URI.
        '''
        # need either a get_one or get to parse args
        method = None
        for name in ('get_one', 'get'):
            if hasattr(self, name):
                method = name
                break
        if not method:
            return

        # get the args to figure out how much to chop off
        args = self._get_args_for_controller(getattr(self, method))
        fixed_args = len(args) - len(
            request.pecan.get('routing_args', [])
        )
        var_args = getargspec(getattr(self, method)).varargs

        # attempt to locate a sub-controller
        if var_args:
            for i, item in enumerate(remainder):
                controller = self._lookup_child(item)
                if controller and not ismethod(controller):
                    self._set_routing_args(request, remainder[:i])
                    return lookup_controller(controller, remainder[i + 1:],
                                             request)
        elif fixed_args < len(remainder) and hasattr(
            self, remainder[fixed_args]
        ):
            controller = self._lookup_child(remainder[fixed_args])
            if not ismethod(controller):
                self._set_routing_args(request, remainder[:fixed_args])
                return lookup_controller(
                    controller,
                    remainder[fixed_args + 1:],
                    request
                )

    def _handle_unknown_method(self, method, remainder, request=None):
        '''
        Routes undefined actions (like RESET) to the appropriate controller.
        '''
        if request is None:
            self._raise_method_deprecation_warning(self._handle_unknown_method)

        # try finding a post_{custom} or {custom} method first
        controller = self._find_controller('post_%s' % method, method)
        if controller:
            return controller, remainder

        # if no controller exists, try routing to a sub-controller; note that
        # since this isn't a safe GET verb, any local exposes are 405'd
        if remainder:
            if self._find_controller(remainder[0]):
                abort(405)
            sub_controller = self._lookup_child(remainder[0])
            if sub_controller:
                return lookup_controller(sub_controller, remainder[1:],
                                         request)

        abort(405)

    def _handle_get(self, method, remainder, request=None):
        '''
        Routes ``GET`` actions to the appropriate controller.
        '''
        if request is None:
            self._raise_method_deprecation_warning(self._handle_get)

        # route to a get_all or get if no additional parts are available
        if not remainder or remainder == ['']:
            remainder = list(six.moves.filter(bool, remainder))
            controller = self._find_controller('get_all', 'get')
            if controller:
                self._handle_bad_rest_arguments(controller, remainder, request)
                return controller, []
            abort(405)

        method_name = remainder[-1]
        # check for new/edit/delete GET requests
        if method_name in ('new', 'edit', 'delete'):
            if method_name == 'delete':
                method_name = 'get_delete'
            controller = self._find_controller(method_name)
            if controller:
                return controller, remainder[:-1]

        match = self._handle_custom_action(method, remainder, request)
        if match:
            return match

        controller = self._lookup_child(remainder[0])
        if controller and not ismethod(controller):
            return lookup_controller(controller, remainder[1:], request)

        # finally, check for the regular get_one/get requests
        controller = self._find_controller('get_one', 'get')
        if controller:
            self._handle_bad_rest_arguments(controller, remainder, request)
            return controller, remainder

        abort(405)

    def _handle_delete(self, method, remainder, request=None):
        '''
        Routes ``DELETE`` actions to the appropriate controller.
        '''
        if request is None:
            self._raise_method_deprecation_warning(self._handle_delete)

        if remainder:
            match = self._handle_custom_action(method, remainder, request)
            if match:
                return match

            controller = self._lookup_child(remainder[0])
            if controller and not ismethod(controller):
                return lookup_controller(controller, remainder[1:], request)

        # check for post_delete/delete requests first
        controller = self._find_controller('post_delete', 'delete')
        if controller:
            return controller, remainder

        # if no controller exists, try routing to a sub-controller; note that
        # since this is a DELETE verb, any local exposes are 405'd
        if remainder:
            if self._find_controller(remainder[0]):
                abort(405)
            sub_controller = self._lookup_child(remainder[0])
            if sub_controller:
                return lookup_controller(sub_controller, remainder[1:],
                                         request)

        abort(405)

    def _handle_post(self, method, remainder, request=None):
        '''
        Routes ``POST`` requests.
        '''
        if request is None:
            self._raise_method_deprecation_warning(self._handle_post)

        # check for custom POST/PUT requests
        if remainder:
            match = self._handle_custom_action(method, remainder, request)
            if match:
                return match

            controller = self._lookup_child(remainder[0])
            if controller and not ismethod(controller):
                return lookup_controller(controller, remainder[1:], request)

        # check for regular POST/PUT requests
        controller = self._find_controller(method)
        if controller:
            return controller, remainder

        abort(405)

    def _handle_put(self, method, remainder, request=None):
        return self._handle_post(method, remainder, request)

    def _handle_custom_action(self, method, remainder, request=None):
        if request is None:
            self._raise_method_deprecation_warning(self._handle_custom_action)

        remainder = [r for r in remainder if r]
        if remainder:
            if method in ('put', 'delete'):
                # For PUT and DELETE, additional arguments are supplied, e.g.,
                # DELETE /foo/XYZ
                method_name = remainder[0]
                remainder = remainder[1:]
            else:
                method_name = remainder[-1]
                remainder = remainder[:-1]
            if method.upper() in self._custom_actions.get(method_name, []):
                controller = self._find_controller(
                    '%s_%s' % (method, method_name),
                    method_name
                )
                if controller:
                    return controller, remainder

    def _set_routing_args(self, request, args):
        '''
        Sets default routing arguments.
        '''
        request.pecan.setdefault('routing_args', []).extend(args)

    def _raise_method_deprecation_warning(self, handler):
        warnings.warn(
            (
                "The function signature for %s.%s.%s is changing "
                "in the next version of pecan.\nPlease update to: "
                "`%s(self, method, remainder, request)`." % (
                    self.__class__.__module__,
                    self.__class__.__name__,
                    handler.__name__,
                    handler.__name__
                )
            ),
            DeprecationWarning
        )
