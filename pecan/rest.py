from inspect import getargspec, ismethod

from core import abort, request
from decorators import expose
from routing import lookup_controller
from util import iscontroller


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

    @expose()
    def _route(self, args):
        '''
        Routes a request to the appropriate controller and returns its result.

        Performs a bit of validation - refuses to route delete and put actions
        via a GET request).
        '''
        # convention uses "_method" to handle browser-unsupported methods
        if request.environ.get('pecan.validation_redirected', False) == True:
            #
            # If the request has been internally redirected due to a validation
            # exception, we want the request method to be enforced as GET, not
            # the `_method` param which may have been passed for REST support.
            #
            method = request.method.lower()
        else:
            method = request.params.get('_method', request.method).lower()

        # make sure DELETE/PUT requests don't use GET
        if request.method == 'GET' and method in ('delete', 'put'):
            abort(405)

        # check for nested controllers
        result = self._find_sub_controllers(args)
        if result:
            return result

        # handle the request
        handler = getattr(self, '_handle_%s' % method, self._handle_custom)
        result = handler(method, args)

        # return the result
        return result

    def _find_controller(self, *args):
        '''
        Returns the appropriate controller for routing a custom action.
        '''
        for name in args:
            obj = getattr(self, name, None)
            if obj and iscontroller(obj):
                return obj
        return None

    def _find_sub_controllers(self, remainder):
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
        args = getargspec(getattr(self, method))
        fixed_args = len(args[0][1:]) - len(
            request.pecan.get('routing_args', [])
        )
        var_args = args[1]

        # attempt to locate a sub-controller
        if var_args:
            for i, item in enumerate(remainder):
                controller = getattr(self, item, None)
                if controller and not ismethod(controller):
                    self._set_routing_args(remainder[:i])
                    return lookup_controller(controller, remainder[i + 1:])
        elif fixed_args < len(remainder) and hasattr(
                self, remainder[fixed_args]
            ):
            controller = getattr(self, remainder[fixed_args])
            if not ismethod(controller):
                self._set_routing_args(remainder[:fixed_args])
                return lookup_controller(
                    controller,
                    remainder[fixed_args + 1:]
                )

    def _handle_custom(self, method, remainder):
        '''
        Routes ``_custom`` actions to the appropriate controller.
        '''
        # try finding a post_{custom} or {custom} method first
        controller = self._find_controller('post_%s' % method, method)
        if controller:
            return controller, remainder

        # if no controller exists, try routing to a sub-controller; note that
        # since this isn't a safe GET verb, any local exposes are 405'd
        if remainder:
            if self._find_controller(remainder[0]):
                abort(405)
            sub_controller = getattr(self, remainder[0], None)
            if sub_controller:
                return lookup_controller(sub_controller, remainder[1:])

        abort(404)

    def _handle_get(self, method, remainder):
        '''
        Routes ``GET`` actions to the appropriate controller.
        '''
        # route to a get_all or get if no additional parts are available
        if not remainder or remainder == ['']:
            controller = self._find_controller('get_all', 'get')
            if controller:
                return controller, []
            abort(404)

        method_name = remainder[-1]
        # check for new/edit/delete GET requests
        if method_name in ('new', 'edit', 'delete'):
            if method_name == 'delete':
                method_name = 'get_delete'
            controller = self._find_controller(method_name)
            if controller:
                return controller, remainder[:-1]

        # check for custom GET requests
        if method.upper() in self._custom_actions.get(method_name, []):
            controller = self._find_controller(
                'get_%s' % method_name,
                method_name
            )
            if controller:
                return controller, remainder[:-1]
        controller = getattr(self, remainder[0], None)
        if controller and not ismethod(controller):
            return lookup_controller(controller, remainder[1:])

        # finally, check for the regular get_one/get requests
        controller = self._find_controller('get_one', 'get')
        if controller:
            return controller, remainder

        abort(404)

    def _handle_delete(self, method, remainder):
        '''
        Routes ``DELETE`` actions to the appropriate controller.
        '''
        # check for post_delete/delete requests first
        controller = self._find_controller('post_delete', 'delete')
        if controller:
            return controller, remainder

        # if no controller exists, try routing to a sub-controller; note that
        # since this is a DELETE verb, any local exposes are 405'd
        if remainder:
            if self._find_controller(remainder[0]):
                abort(405)
            sub_controller = getattr(self, remainder[0], None)
            if sub_controller:
                return lookup_controller(sub_controller, remainder[1:])

        abort(404)

    def _handle_post(self, method, remainder):
        '''
        Routes ``POST`` requests.
        '''
        # check for custom POST/PUT requests
        if remainder:
            method_name = remainder[-1]
            if method.upper() in self._custom_actions.get(method_name, []):
                controller = self._find_controller(
                    '%s_%s' % (method, method_name),
                    method_name
                )
                if controller:
                    return controller, remainder[:-1]
            controller = getattr(self, remainder[0], None)
            if controller and not ismethod(controller):
                return lookup_controller(controller, remainder[1:])

        # check for regular POST/PUT requests
        controller = self._find_controller(method)
        if controller:
            return controller, remainder

        abort(404)

    _handle_put = _handle_post

    def _set_routing_args(self, args):
        '''
        Sets default routing arguments.
        '''
        request.pecan.setdefault('routing_args', []).extend(args)
