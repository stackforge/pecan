from templating import renderers
from webob      import Request, Response, exc
from threading  import local
from routing    import lookup_controller

import string


state = local()


class RequestWrapper(object):
    def __getattr__(self, attr):
        return getattr(state.request, attr)
    def __setattr__(self, attr, value):
        return setattr(state.request, attr, value)


request = RequestWrapper()


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
        self.translate        = string.maketrans(
            string.punctuation, 
            '_' * len(string.punctuation)
        )
    
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
        
    def __call__(self, environ, start_response):
        # create the request object
        state.request = Request(environ)
        
        # lookup the controller
        path = state.request.path
        content_type = None
        if '.' in path.split('/')[-1]:
            path, format = path.split('.')
            override_content_type = True
            content_type = self.get_content_type(format)      
        controller = self.route(self.root, path)
        
        # if we didn't find a controller, issue a 404
        if controller is None:
            response = Response()
            response.status = 404
            return response(environ, start_response)
        
        # determine content type
        if content_type is None:
            content_type = controller.pecan.get('content_type', 'text/html')
        
        # handle "before" hooks
        for hook in self.hooks:
            hook.before(state)
        
        # get the result from the controller, properly handling wrap hooks
        try:
            result = controller(**dict(state.request.str_params))
                        
            # pull the template out based upon content type
            template = controller.pecan.get('content_types', {}).get(content_type)
        
            # handle template overrides
            template = getattr(request, 'override_template', template)
        
            if template:
                renderer = self.renderers.get(self.default_renderer, self.template_path)
                if template == 'json':
                    renderer = self.renderers.get('json', self.template_path)
                elif ':' in template:
                    renderer = self.renderers.get(template.split(':')[0], self.template_path)
                    template = template.split(':')[1]
                result = renderer.render(template, result)
                content_type = renderer.content_type
        
            response = Response(result)
            if content_type:
                response.content_type = content_type
        except Exception, e:
            # handle "error" hooks
            for hook in self.hooks:
                hook.on_error(state, e)
            raise
        else:
            # handle "after" hooks
            for hook in self.hooks:
                hook.after(state)
            
            return response(environ, start_response)
        finally:
            del state.request