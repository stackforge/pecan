from templating import renderers
from routing    import lookup_controller

from webob      import Request, Response, exc
from threading  import local
from itertools  import chain


state = local()


def proxy(key):
    class ObjectProxy(object):
        def __getattr__(self, attr):
            obj = getattr(state, key)
            return getattr(obj, attr)
        def __setattr__(self, attr, value):
            obj = getattr(state, key)
            return setattr(obj, attr, value)
    return ObjectProxy()


request  = proxy('request')
response = proxy('response')


def override_template(template):
    request.override_template = template


class Pecan(object):
    def __init__(self, root, 
                 renderers        = renderers, 
                 default_renderer = 'genshi', 
                 template_path    = 'templates', 
                 hooks            = []):
        
        self.root             = root
        self.renderers        = renderers
        self.default_renderer = default_renderer
        self.hooks            = hooks
        self.template_path    = template_path
    
    def get_content_type(self, format):
        return {
            'html'  : 'text/html',
            'xhtml' : 'text/html',
            'json'  : 'application/json'
        }.get(format, 'text/html')
    
    def route(self, node, path):
        path = path.split('/')[1:]
        node, remainder = lookup_controller(node, path)        
        return node
    
    def handle_security(self, controller):
        if controller.pecan.get('secured', False):
            if not controller.pecan['check_permissions']():
                raise exc.HTTPUnauthorized
    
    def determine_hooks(self, controller):
        return list(
            sorted(
                chain(controller.pecan.get('hooks', []), self.hooks), 
                lambda x,y: cmp(x.priority, y.priority)
            )
        )
    
    def handle_hooks(self, hook_type, *args):
        for hook in state.hooks:
            getattr(hook, hook_type)(*args)
    
    def handle_request(self):
        # lookup the controller, respecting content-type as requested
        # by the file extension on the URI
        path = state.request.path
        content_type = None
        if '.' in path.split('/')[-1]:
            path, format = path.split('.')
            content_type = self.get_content_type(format)      
        controller = self.route(self.root, path)
    
        # determine content type
        if content_type is None:
            content_type = controller.pecan.get('content_type', 'text/html')
    
        # handle security
        self.handle_security(controller)
        
        # get a sorted list of hooks, by priority
        state.hooks = self.determine_hooks(controller)    
    
        # handle "before" hooks
        self.handle_hooks('before', state)
    
        # get the result from the controller, properly handling wrap hooks
        result = controller(**dict(state.request.str_params))
                    
        # pull the template out based upon content type and handle overrides
        template = controller.pecan.get('content_types', {}).get(content_type)
        template = getattr(request, 'override_template', template)
        
        # if there is a template, render it
        if template:
            renderer = self.renderers.get(self.default_renderer, self.template_path)
            if template == 'json':
                renderer = self.renderers.get('json', self.template_path)
            elif ':' in template:
                renderer = self.renderers.get(template.split(':')[0], self.template_path)
                template = template.split(':')[1]
            result = renderer.render(template, result)
            content_type = renderer.content_type
        
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
        state.request = Request(environ)
        state.response = Response()
        state.hooks = []
        
        # handle the request
        try:
            self.handle_request()
        except Exception, e:
            # if this is an HTTP Exception, set it as the response
            if isinstance(e, exc.HTTPException):
                state.response = e
            
            # handle "error" hooks
            self.handle_hooks('on_error', state, e)
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