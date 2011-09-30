from templating         import RendererFactory
from routing            import lookup_controller, NonCanonicalPath
from util               import _cfg, splitext, encode_if_needed

from webob              import Request, Response, exc
from threading          import local
from itertools          import chain
from mimetypes          import guess_type, add_type
from formencode         import htmlfill, Invalid, variabledecode
from formencode.schema  import merge_dicts
from paste.recursive    import ForwardRequestException
from urlparse           import urlsplit, urlunsplit

try:
    from simplejson import loads
except ImportError: # pragma: no cover
    from json import loads

import urllib

# make sure that json is defined in mimetypes
add_type('application/json', '.json', True)

state = local()


def proxy(key):
    class ObjectProxy(object):
        def __getattr__(self, attr):
            obj = getattr(state, key)
            return getattr(obj, attr)
        def __setattr__(self, attr, value):
            obj = getattr(state, key)
            return setattr(obj, attr, value)
        def __delattr__(self, attr):
            obj = getattr(state, key)
            return delattr(obj, attr)
    return ObjectProxy()


request     = proxy('request')
response    = proxy('response')


def override_template(template, content_type=None):
    '''
    Call within a controller to override the template that is used in
    your response.
    
    :param template: a valid path to a template file, just as you would specify in an ``@expose``.
    :param content_type: a valid MIME type to use for the response.
    '''
    
    request.pecan['override_template'] = template
    if content_type:
        request.pecan['override_content_type'] = content_type 


def abort(status_code=None, detail='', headers=None, comment=None, **kw):
    '''
    Raise an HTTP status code, as specified. Useful for returning status
    codes like 401 Unauthorized or 403 Forbidden.
    
    :param status_code: The HTTP status code as an integer.
    :param detail: The message to send along, as a string.
    :param headers: A dictionary of headers to send along with the response.
    :param comment: A comment to include in the response.
    '''
    
    raise exc.status_map[status_code](detail=detail, headers=headers, comment=comment, **kw)


def redirect(location=None, internal=False, code=None, headers={}, add_slash=False):
    '''
    Perform a redirect, either internal or external. An internal redirect
    performs the redirect server-side, while the external redirect utilizes
    an HTTP 302 status code.
    
    :param location: The HTTP location to redirect to.
    :param internal: A boolean indicating whether the redirect should be internal.
    :param code: The HTTP status code to use for the redirect. Defaults to 302.
    :param headers: Any HTTP headers to send with the response, as a dictionary.
    '''
    
    if add_slash:
        if location is None:
            split_url = list(urlsplit(state.request.url))
            new_proto = state.request.environ.get('HTTP_X_FORWARDED_PROTO', split_url[0])
            split_url[0] = new_proto
        else:
            split_url = urlsplit(location)

        split_url[2] = split_url[2].rstrip('/') + '/'
        location = urlunsplit(split_url)

    if not headers:
        headers = {}
    if internal:
        if code is not None:
            raise ValueError('Cannot specify a code for internal redirects')
        raise ForwardRequestException(location)
    if code is None:
        code = 302
    raise exc.status_map[code](location=location, headers=headers)


def error_for(field):
    '''
    A convenience function for fetching the validation error for a
    particular field in a form. Useful within templates when not using
    ``htmlfill`` for forms.
    
    :param field: The name of the field to get the error for.
    '''
    
    return request.pecan['validation_errors'].get(field, '')


def static(name, value):
    '''
    When using ``htmlfill`` validation support, this function indicates
    that ``htmlfill`` should not fill in a value for this field, and
    should instead use the value specified.
    
    :param name: The name of the field.
    :param value: The value to specify.
    '''
    
    if 'pecan.params' not in request.environ:
        request.environ['pecan.params'] = dict(request.params)    
    request.environ['pecan.params'][name] = value
    return value


def render(template, namespace):
    '''
    Render the specified template using the Pecan rendering framework
    with the specified template namespace as a dictionary. Useful in a
    controller where you have no template specified in the ``@expose``.
    
    :param template: The path to your template, as you would specify in ``@expose``.
    :param namespace: The namespace to use for rendering the template, as a dictionary.
    '''
    
    return state.app.render(template, namespace)


class ValidationException(ForwardRequestException):
    '''
    This exception is raised when a validation error occurs using Pecan's
    built-in validation framework.
    '''
    
    def __init__(self, location=None, errors={}):
        if state.controller is not None:
            cfg = _cfg(state.controller)
        else:
            cfg = {}
        if location is None and 'error_handler' in cfg:
            location = cfg['error_handler']
            if callable(location):
                location = location()
        merge_dicts(request.pecan['validation_errors'], errors)
        if 'pecan.params' not in request.environ:
            request.environ['pecan.params'] = dict(request.params)
        request.environ['pecan.validation_errors'] = request.pecan['validation_errors']
        if cfg.get('htmlfill') is not None:
            request.environ['pecan.htmlfill'] = cfg['htmlfill']
        request.environ['REQUEST_METHOD'] = 'GET'
        request.environ['pecan.validation_redirected'] = True
        ForwardRequestException.__init__(self, location)


class Pecan(object):
    '''
    Base Pecan application object. Generally created using ``pecan.make_app``,
    rather than being created manually.
    '''
    
    def __init__(self, root, 
                 default_renderer    = 'mako', 
                 template_path       = 'templates', 
                 hooks               = [],
                 custom_renderers    = {},
                 extra_template_vars = {},
                 force_canonical     = True
                 ):
        '''
        Creates a Pecan application instance, which is a WSGI application.
        
        :param root: The root controller object.
        :param default_renderer: The default rendering engine to use. Defaults to mako.
        :param template_path: The default relative path to use for templates. Defaults to 'templates'.
        :param hooks: A list of Pecan hook objects to use for this application.
        :param custom_renderers: Custom renderer objects, as a dictionary keyed by engine name.
        :param extra_template_vars: Any variables to inject into the template namespace automatically.
        :param force_canonical: A boolean indicating if this project should require canonical URLs.
        '''

        self.root             = root
        self.renderers        = RendererFactory(custom_renderers, extra_template_vars)
        self.default_renderer = default_renderer
        self.hooks            = hooks
        self.template_path    = template_path
        self.force_canonical  = force_canonical
        
    def route(self, node, path):
        '''
        Looks up a controller from a node based upon the specified path.
        
        :param node: The node, such as a root controller object.
        :param path: The path to look up on this node.
        '''
        
        path = path.split('/')[1:]
        try:
            node, remainder = lookup_controller(node, path)
            return node, remainder
        except NonCanonicalPath, e:
            if self.force_canonical and not _cfg(e.controller).get('accept_noncanonical', False):
                if request.method == 'POST':
                    raise RuntimeError, "You have POSTed to a URL '%s' which '\
                        'requires a slash. Most browsers will not maintain '\
                        'POST data when redirected. Please update your code '\
                        'to POST to '%s/' or set force_canonical to False" % \
                        (request.pecan['routing_path'], request.pecan['routing_path'])
                redirect(code=302, add_slash=True)
            return e.controller, e.remainder
    
    def determine_hooks(self, controller=None):
        '''
        Determines the hooks to be run, in which order.
        
        :param controller: If specified, includes hooks for a specific controller.
        '''
        
        controller_hooks = []
        if controller:
            controller_hooks = _cfg(controller).get('hooks', [])
        return list(
            sorted(
                chain(controller_hooks, self.hooks), 
                lambda x,y: cmp(x.priority, y.priority)
            )
        )
    
    def handle_hooks(self, hook_type, *args):
        '''
        Processes hooks of the specified type.
        
        :param hook_type: The type of hook, including ``before``, ``after``, ``on_error``, and ``on_route``.
        :param *args: Arguments to pass to the hooks.
        '''
        
        if hook_type in ['before', 'on_route']:
            hooks = state.hooks
        else:
            hooks = reversed(state.hooks)

        for hook in hooks:
             getattr(hook, hook_type)(*args)

    def get_args(self, all_params, remainder, argspec, im_self):
        '''
        Determines the arguments for a controller based upon parameters
        passed the argument specification for the controller.
        '''
        args = []
        kwargs = dict()
        valid_args = argspec[0][1:]

        def _decode(x):
            return urllib.unquote_plus(x) if isinstance(x, basestring) else x
    
        remainder = [_decode(x) for x in remainder]
        
        if im_self is not None:
            args.append(im_self)
        
        # grab the routing args from nested REST controllers
        if 'routing_args' in request.pecan:
            remainder = request.pecan['routing_args'] + list(remainder)
            del request.pecan['routing_args']
        
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
        
        # get the default positional arguments
        if argspec[3]:
            defaults = dict(zip(argspec[0][-len(argspec[3]):], argspec[3]))
        else:
            defaults = dict()
        
        # handle positional GET/POST params
        for name in valid_args:
            if name in all_params:
                args.append(all_params.pop(name))
            elif name in defaults:
                args.append(defaults[name])
            else:
                break
        
        # handle wildcard GET/POST params
        if argspec[2]:
            for name, value in all_params.iteritems():
                if name not in argspec[0]:
                    kwargs[encode_if_needed(name)] = value
        
        return args, kwargs
    
    def render(self, template, namespace):
        renderer = self.renderers.get(self.default_renderer, self.template_path)
        if template == 'json':
            renderer = self.renderers.get('json', self.template_path)
        else:
            namespace['error_for'] = error_for
            namespace['static'] = static
        if ':' in template:
            renderer = self.renderers.get(template.split(':')[0], self.template_path)
            template = template.split(':')[1]
        return renderer.render(template, namespace)
    
    def validate(self, schema, params, json=False, error_handler=None, 
                 htmlfill=None, variable_decode=None):
        '''
        Performs validation against a schema for any passed params, 
        including support for ``JSON``.
        
        :param schema: A ``formencode`` ``Schema`` object to validate against.
        :param params: The dictionary of parameters to validate.
        :param json: A boolean, indicating whether or not the validation should validate against JSON content.
        :param error_handler: The path to a controller which will handle errors. If not specified, validation errors will raise a ``ValidationException``.
        :param htmlfill: Specifies whether or not to use htmlfill.
        :param variable_decode: Indicates whether or not to decode variables when using htmlfill.
        '''
        
        try:
            to_validate = params
            if json:
                to_validate = loads(request.body)
            if variable_decode is not None:
                to_validate = variabledecode.variable_decode(to_validate, **variable_decode)
            params = schema.to_python(to_validate)
        except Invalid, e:
            kwargs = {}
            if variable_decode is not None:
                kwargs['encode_variables'] = True
                kwargs.update(variable_decode)
            request.pecan['validation_errors'] = e.unpack_errors(**kwargs)
            if error_handler is not None:
                raise ValidationException()
        if json:
            params = dict(data=params)
        return params
    
    def handle_request(self):
        '''
        The main request handler for Pecan applications.
        '''
        
        # get a sorted list of hooks, by priority (no controller hooks yet)
        state.hooks = self.determine_hooks()
        
        # store the routing path to allow hooks to modify it
        request.pecan['routing_path'] = request.path

        # handle "on_route" hooks
        self.handle_hooks('on_route', state)
        
        # lookup the controller, respecting content-type as requested
        # by the file extension on the URI
        path = request.pecan['routing_path']

        if not request.pecan['content_type'] and '.' in path.split('/')[-1]:
            path, extension = splitext(path)
            request.pecan['extension'] = extension
            # preface with a letter to ensure compat for 2.5
            request.pecan['content_type'] = guess_type('x' + extension)[0]

        controller, remainder = self.route(self.root, path)
        cfg = _cfg(controller)

        if cfg.get('generic_handler'):
            raise exc.HTTPNotFound
        
        # handle generic controllers
        im_self = None
        if cfg.get('generic'):
            im_self = controller.im_self
            handlers = cfg['generic_handlers']
            controller = handlers.get(request.method, handlers['DEFAULT'])
            cfg = _cfg(controller)
                    
        # add the controller to the state so that hooks can use it
        state.controller = controller
    
        # if unsure ask the controller for the default content type 
        if not request.pecan['content_type']:
            request.pecan['content_type'] = cfg.get('content_type', 'text/html')
        elif cfg.get('content_type') is not None and \
            request.pecan['content_type'] not in cfg.get('content_types', {}):

            print "Controller '%s' defined does not support content_type '%s'. Supported type(s): %s" % (
                controller.__name__,
                request.pecan['content_type'],
                cfg.get('content_types', {}).keys()
                )
            raise exc.HTTPNotFound
        
        # get a sorted list of hooks, by priority
        state.hooks = self.determine_hooks(controller)
    
        # handle "before" hooks
        self.handle_hooks('before', state)
        
        # fetch and validate any parameters
        params = dict(request.params)
        if 'schema' in cfg:
            params = self.validate(
                        cfg['schema'], 
                        params, 
                        json=cfg['validate_json'], 
                        error_handler=cfg.get('error_handler'), 
                        htmlfill=cfg.get('htmlfill'),
                        variable_decode=cfg.get('variable_decode')
                    )
        elif 'pecan.validation_errors' in request.environ:
            request.pecan['validation_errors'] = request.environ.pop('pecan.validation_errors')
        
        # fetch the arguments for the controller
        args, kwargs = self.get_args(
            params, 
            remainder,
            cfg['argspec'],
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
        template = cfg.get('content_types', {}).get(request.pecan['content_type'])

        # check if for controller override of template
        template = request.pecan.get('override_template', template)
        request.pecan['content_type'] = request.pecan.get('override_content_type', request.pecan['content_type'])

        # if there is a template, render it
        if template:
            if template == 'json':
                request.pecan['content_type'] = 'application/json'
            result = self.render(template, result)
        
        # pass the response through htmlfill (items are popped out of the 
        # environment even if htmlfill won't run for proper cleanup)
        _htmlfill = cfg.get('htmlfill')
        if _htmlfill is None and 'pecan.htmlfill' in request.environ:
            _htmlfill = request.environ.pop('pecan.htmlfill')
        if 'pecan.params' in request.environ:
            params = request.environ.pop('pecan.params')
        if request.pecan['validation_errors'] and _htmlfill is not None and request.pecan['content_type'] == 'text/html':
            errors = request.pecan['validation_errors']
            result = htmlfill.render(result, defaults=params, errors=errors, text_as_default=True, **_htmlfill)
        
        # If we are in a test request put the namespace where it can be
        # accessed directly
        if request.environ.get('paste.testing'):
            testing_variables = request.environ['paste.testing_variables']
            testing_variables['namespace'] = raw_namespace
            testing_variables['template_name'] = template
            testing_variables['controller_output'] = result
        
        # set the body content
        if isinstance(result, unicode):
            response.unicode_body = result
        else:
            response.body = result
        
        # set the content type
        if request.pecan['content_type']:
            response.content_type = request.pecan['content_type']
    
    def __call__(self, environ, start_response):
        '''
        Implements the WSGI specification for Pecan applications, utilizing ``WebOb``.
        '''
        
        # create the request and response object
        state.request      = Request(environ)
        state.response     = Response()
        state.hooks        = []
        state.app          = self
        state.controller   = None
        
        # handle the request
        try:
            # add context and environment to the request 
            state.request.context = {}
            state.request.pecan = dict(content_type=None, validation_errors={})

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
            del state.hooks
            del state.request
            del state.response
            del state.controller
