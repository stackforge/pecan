from templating import renderers
from webob      import Request, Response, exc
from threading  import local

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
    def __init__(self, root, renderers=renderers, default_renderer='genshi', hooks=[]):
        self.root             = root
        self.renderers        = renderers
        self.default_renderer = default_renderer
        self.hooks            = hooks
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

        curpath      = ""
        nodeconf     = {}
        object_trail = [['root', self.root, nodeconf, curpath]]
        
        names     = [x for x in path.strip('/').split('/') if x] + ['index']
        iternames = names[:]
        while iternames:
            name     = iternames[0]
            objname  = name.translate(self.translate)            
            nodeconf = {}
            subnode  = getattr(node, objname, None)
            name     = iternames.pop(0)
            node     = subnode
            curpath  = "/".join((curpath, name))            
            object_trail.append([name, node, nodeconf, curpath])
        
        # try successive objects (reverse order)
        num_candidates = len(object_trail) - 1
        for i in range(num_candidates, -1, -1):
            name, candidate, nodeconf, curpath = object_trail[i]
            if candidate is None:
                continue
            
            # try a "_route" method on the current leaf.
            if hasattr(candidate, "_route"):
                processed_path = object_trail[i][-1]
                unprocessed_path = object_trail[-1][-1].replace(processed_path, '')
                return candidate._route(unprocessed_path)
            
            # try a "_lookup" method on the current leaf.
            if hasattr(candidate, "_lookup"):
                lookup = candidate._lookup(object_trail[i+1][0])
                processed_path = object_trail[i+1][-1]
                unprocessed_path = object_trail[-2][-1].replace(processed_path, '')
                return self.route(lookup, unprocessed_path)
            
            # try a "_default" method on the current leaf.
            if hasattr(candidate, "_default"):
                defhandler = candidate._default
                if getattr(defhandler, 'exposed', False):
                    object_trail.insert(i+1, ["_default", defhandler, {}, curpath])
                    return defhandler
                        
            # try the current leaf.
            if getattr(candidate, 'exposed', False):
                return candidate
        
        # we didn't find anything
        return None
    
    def __call__(self, environ, start_response):
        # create the request object
        state.request = Request(environ)
        
        # lookup the controller
        path = state.request.path
        content_type = 'text/html'
        if '.' in path.split('/')[-1]:
            path, format = path.split('.')
            content_type = self.get_content_type(format)
        controller = self.route(self.root, path)
        
        # if we didn't find a controller, issue a 404
        if controller is None:
            response = Response()
            response.status = 404
            return response(environ, start_response)
        
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
                renderer = self.renderers[self.default_renderer]
                if template == 'json':
                    renderer = self.renderers['json']
                elif len(self.renderers) > 1 and ':' in template:
                    renderer = self.renderers.get(template.split(':')[0], self.renderers.values()[0])
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