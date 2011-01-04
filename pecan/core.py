from configuration      import _runtime_conf
from monitor            import MonitorableProcess
from templating         import RendererFactory
from routing            import lookup_controller

from webob              import Request, Response, exc
from threading          import local
from itertools          import chain
from formencode         import Invalid
from paste.recursive    import ForwardRequestException


try:
    from json import loads
except ImportError:
    from simplejson import loads


state = local()


def proxy(key):
    class ObjectProxy(object):
        def __getattr__(self, attr):
            obj = getattr(state, key)
            if attr == 'validation_error':
                return getattr(obj, attr, None)
            return getattr(obj, attr)
        def __setattr__(self, attr, value):
            obj = getattr(state, key)
            return setattr(obj, attr, value)
    return ObjectProxy()


request     = proxy('request')
context     = proxy('request.context')
response    = proxy('response')


def override_template(template):
    request.override_template = template


def abort(status_code=None, detail='', headers=None, comment=None):
    raise exc.status_map[status_code](detail=detail, headers=headers, comment=comment)


def redirect(location, internal=False, code=None):
    if internal:
        if code is not None:
            raise ValueError('Cannot specify a code for internal redirects')
        raise ForwardRequestException(location)
    if code is None:
        code = 302
    raise exc.status_map[code](location=location)


def error_for(field):
    if request.validation_error is None: return ''
    return request.validation_error.error_dict.get(field, '')


class Pecan(MonitorableProcess):
    def __init__(self, root, 
                 default_renderer    = 'mako', 
                 template_path       = 'templates', 
                 hooks               = [],
                 custom_renderers    = {},
                 extra_template_vars = {}
                 ):
        
        self.root             = root
        self.renderers        = RendererFactory(custom_renderers, extra_template_vars)
        self.default_renderer = default_renderer
        self.hooks            = hooks
        self.template_path    = template_path
        
        MonitorableProcess.__init__(self)
        if getattr(_runtime_conf, 'app', None) and getattr(_runtime_conf.app, 'reload', False) is True:
            self.start_monitoring()
    
    def get_content_type(self, format):
        return {
            'html'  : 'text/html',
            'xhtml' : 'text/html',
            'json'  : 'application/json'
        }.get(format, 'text/html')
    
    def route(self, node, path):
        path = path.split('/')[1:]
        node, remainder = lookup_controller(node, path)        
        return node, remainder
    
    def handle_security(self, controller):
        if controller.pecan.get('secured', False):
            if not controller.pecan['check_permissions']():
                raise exc.HTTPUnauthorized
    
    def determine_hooks(self, controller=None):
        controller_hooks = []
        if controller:
            controller_hooks = controller.pecan.get('hooks', [])
        return list(
            sorted(
                chain(controller_hooks, self.hooks), 
                lambda x,y: cmp(x.priority, y.priority)
            )
        )
    
    def handle_hooks(self, hook_type, *args):
        if hook_type in ['before', 'on_route']:
            hooks = state.hooks
        else:
            hooks = reversed(state.hooks)

        for hook in hooks:
             getattr(hook, hook_type)(*args)

    def get_params(self, all_params, remainder, argspec, im_self):
        valid_params = dict()
        positional_params = []
        
        if im_self is not None:
            positional_params.append(im_self)
        
        # handle params that are POST or GET variables first
        for param_name, param_value in all_params.iteritems():
            if param_name in argspec[0]:
                valid_params[param_name] = param_value
        
        # handle positional arguments
        used = set()
        for i, value in enumerate(remainder):
            if len(argspec.args) > (i+1):
                if valid_params.get(argspec.args[i+1]) is None:
                    used.add(i)
                    valid_params[argspec.args[i+1]] = value
        
        # handle unconsumed positional arguments
        if len(used) < len(remainder) and argspec.varargs is not None:
            for i, value in enumerate(remainder):
                if i not in used:
                    positional_params.append(value)
        
        return valid_params, positional_params
    
    def validate(self, schema, params=None, json=False):
        to_validate = params
        if json:
            to_validate = loads(request.body)
        return schema.to_python(to_validate)
        
    def handle_request(self):
        
        # get a sorted list of hooks, by priority (no controller hooks yet)
        state.hooks = self.determine_hooks()
        
        # handle "on_route" hooks
        self.handle_hooks('on_route', state)
        
        # lookup the controller, respecting content-type as requested
        # by the file extension on the URI
        path = state.request.path
        content_type = None
        if '.' in path.split('/')[-1]:
            path, format = path.split('.')
            content_type = self.get_content_type(format)      
        controller, remainder = self.route(self.root, path)
        
        if controller.pecan.get('generic_handler'):
            raise exc.HTTPNotFound
        
        # handle generic controllers
        im_self = None
        if controller.pecan.get('generic'):
            im_self = controller.im_self
            handlers = controller.pecan['generic_handlers']
            controller = handlers.get(request.method, handlers['DEFAULT'])
                    
        # add the controller to the state so that hooks can use it
        state.controller = controller
    
        # determine content type
        if content_type is None:
            content_type = controller.pecan.get('content_type', 'text/html')
        
        # get a sorted list of hooks, by priority
        state.hooks = self.determine_hooks(controller)    
    
        # handle "before" hooks
        self.handle_hooks('before', state)
        
        # handle security
        self.handle_security(controller)        
    
        # fetch and validate any parameters
        params, positional_params = self.get_params(
            dict(state.request.str_params), 
            remainder,
            controller.pecan['argspec'],
            im_self
        )
        if 'schema' in controller.pecan:
            request.validation_error = None
            try:
                params = self.validate(
                    controller.pecan['schema'], 
                    json   = controller.pecan['validate_json'],
                    params = params
                )
            except Invalid, e:
                request.validation_error = e
                if controller.pecan['error_handler'] is not None:
                    redirect(controller.pecan['error_handler'], internal=True)
            if controller.pecan['validate_json']: params = dict(data=params)
        
        # get the result from the controller
        result = controller(*positional_params, **params)
        raw_namespace = result
        
        # pull the template out based upon content type and handle overrides
        template = controller.pecan.get('content_types', {}).get(content_type)
        template = getattr(request, 'override_template', template)
        
        # if there is a template, render it
        if template:
            renderer = self.renderers.get(self.default_renderer, self.template_path)
            if template == 'json':
                renderer = self.renderers.get('json', self.template_path)
            else:
                result['error_for'] = error_for
                
            if ':' in template:
                renderer = self.renderers.get(template.split(':')[0], self.template_path)
                template = template.split(':')[1]
            result = renderer.render(template, result)
            content_type = renderer.content_type
        
        # If we are in a test request put the namespace where it can be
        # accessed directly
        if request.environ.get('paste.testing'):
            testing_variables = request.environ['paste.testing_variables']
            testing_variables['namespace'] = raw_namespace
            testing_variables['template_name'] = template
            testing_variables['controller_output'] = result
        
        # set the body content
        if isinstance(result, unicode):
            state.response.unicode_body = result
        else:
            state.response.body = result
        
        # set the content type
        if content_type:
            state.response.content_type = content_type
    
    def __call__(self, environ, start_response):
        # create the request and response object
        state.request  = Request(environ)
        state.response = Response()
        state.hooks    = []
        state.app      = self
        
        # handle the request
        try:
            # add context to the request 
            state.request.context = {}

            self.handle_request()
        except Exception, e:
            # if this is an HTTP Exception, set it as the response
            if isinstance(e, exc.HTTPException):
                state.response = e
            
            # if this is not an internal redirect, run error hooks
            if not isinstance(e, ForwardRequestException):
                self.handle_hooks('on_error', state, e)
            
            if not isinstance(e, exc.HTTPException):
                raise
        finally:
            # handle "after" hooks
            self.handle_hooks('after', state)
            
        # get the response
        try:
            return state.response(environ, start_response)
        finally:        
            # clean up state
            del state.request
            del state.response
            del state.hooks
            if hasattr(state, 'controller'):
                del state.controller
