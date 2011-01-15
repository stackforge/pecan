from configuration      import _runtime_conf
from templating         import RendererFactory
from routing            import lookup_controller

from webob              import Request, Response, exc
from threading          import local
from itertools          import chain
from formencode         import Invalid
from paste.recursive    import ForwardRequestException

try:
    from simplejson import loads
except ImportError:
    from json import loads

import os


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


class Pecan(object):
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
        
    def get_content_type(self, format):
        return {
            '.html'  : 'text/html',
            '.xhtml' : 'text/html',
            '.json'  : 'application/json',
            '.txt'   : 'text/plain'
        }.get(format)
    
    def route(self, node, path):
        path = path.split('/')[1:]
        node, remainder = lookup_controller(node, path)        
        return node, remainder
    
    def determine_hooks(self, controller=None):
        controller_hooks = []
        if controller:
            controller_hooks = controller._pecan.get('hooks', [])
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

    def get_args(self, all_params, remainder, argspec, im_self):
        args = []
        kwargs = dict()
        valid_args = argspec[0][1:]
        
        if im_self is not None:
            args.append(im_self)
        
        # grab the routing args from nested REST controllers
        if 'routing_args' in request.context:
            remainder = request.context.pop('routing_args') + list(remainder)
        
        # handle positional arguments
        if valid_args and remainder:
            args.extend(remainder[:len(valid_args)])
            remainder = remainder[len(valid_args):]
            valid_args = valid_args[len(args):]
        
        # handle wildcard arguments
        if remainder:
            if not argspec[1]:
                abort(404)
            args.extend(remainder)
        
        # handle positional GET/POST params
        for name in valid_args:
            if name in all_params:
                args.append(all_params.pop(name))
        
        # handle wildcard GET/POST params
        if argspec[2]:
            for name, value in all_params.iteritems():
                if name not in argspec[0]:
                    kwargs[name] = value
        
        return args, kwargs
    
    def validate(self, schema, params=None, json=False):
        to_validate = params
        if json:
            to_validate = loads(request.body)
        return schema.to_python(to_validate)
        
    def handle_request(self):
        
        # get a sorted list of hooks, by priority (no controller hooks yet)
        state.hooks = self.determine_hooks()
        state.content_type = None

        # handle "on_route" hooks
        self.handle_hooks('on_route', state)
        
        # lookup the controller, respecting content-type as requested
        # by the file extension on the URI
        path = state.request.path

        if state.content_type is None and '.' in path.split('/')[-1]:
            path, format = os.path.splitext(path)
            # store the extension for retrieval by controllers
            request.context['extension'] = format
            state.content_type = self.get_content_type(format)      
        controller, remainder = self.route(self.root, path)

        if controller._pecan.get('generic_handler'):
            raise exc.HTTPNotFound
        
        # handle generic controllers
        im_self = None
        if controller._pecan.get('generic'):
            im_self = controller.im_self
            handlers = controller._pecan['generic_handlers']
            controller = handlers.get(request.method, handlers['DEFAULT'])
                    
        # add the controller to the state so that hooks can use it
        state.controller = controller
    
        # if unsure ask the controller for the default content type 
        if state.content_type is None:
            state.content_type = controller._pecan.get('content_type', 'text/html')
        # get a sorted list of hooks, by priority
        state.hooks = self.determine_hooks(controller)    
    
        # handle "before" hooks
        self.handle_hooks('before', state)
        
        # fetch and validate any parameters
        params = dict(state.request.str_params)
        if 'schema' in controller._pecan:
            request.validation_error = None
            try:
                params = self.validate(
                    controller._pecan['schema'], 
                    json   = controller._pecan['validate_json'],
                    params = params
                )
            except Invalid, e:
                request.validation_error = e
                if controller._pecan['error_handler'] is not None:
                    redirect(controller._pecan['error_handler'], internal=True)
            if controller._pecan['validate_json']: params = dict(data=params)
        
        # fetch the arguments for the controller
        args, kwargs = self.get_args(
            params, 
            remainder,
            controller._pecan['argspec'],
            im_self
        )
        
        # get the result from the controller
        result = controller(*args, **kwargs)

        # a controller can return the response object which means they've taken 
        # care of filling it out
        if result == response:
            return

        raw_namespace = result

        # pull the template out based upon content type and handle overrides
        template = controller._pecan.get('content_types', {}).get(state.content_type)
        template = getattr(request, 'override_template', template)

        # if there is a template, render it
        if template:
            renderer = self.renderers.get(self.default_renderer, self.template_path)
            if template == 'json':
                renderer = self.renderers.get('json', self.template_path)
                state.content_type = self.get_content_type('json')
            else:
                result['error_for'] = error_for
                
            if ':' in template:
                renderer = self.renderers.get(template.split(':')[0], self.template_path)
                template = template.split(':')[1]
            result = renderer.render(template, result)
        
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
        if state.content_type:
            state.response.content_type = state.content_type
    
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
            del state.content_type
            del state.hooks
            del state.request
            del state.response
            if hasattr(state, 'controller'):
                del state.controller
