try:
    from simplejson import loads
except ImportError:             # pragma: no cover
    from json import loads      # noqa
from threading import local
from itertools import chain
from mimetypes import guess_type, add_type
from os.path import splitext
import logging
import operator

import six

from webob import Request, Response, exc, acceptparse

from .compat import urlparse, unquote_plus, izip
from .secure import handle_security
from .templating import RendererFactory
from .routing import lookup_controller, NonCanonicalPath
from .util import _cfg, encode_if_needed
from .middleware.recursive import ForwardRequestException


# make sure that json is defined in mimetypes
add_type('application/json', '.json', True)

state = local()
logger = logging.getLogger(__name__)


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

        def __dir__(self):
            obj = getattr(state, key)
            return dir(obj)

    return ObjectProxy()


request = proxy('request')
response = proxy('response')


def override_template(template, content_type=None):
    '''
    Call within a controller to override the template that is used in
    your response.

    :param template: a valid path to a template file, just as you would specify
                     in an ``@expose``.
    :param content_type: a valid MIME type to use for the response.func_closure
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

    raise exc.status_map[status_code](
        detail=detail,
        headers=headers,
        comment=comment,
        **kw
    )


def redirect(location=None, internal=False, code=None, headers={},
             add_slash=False):
    '''
    Perform a redirect, either internal or external. An internal redirect
    performs the redirect server-side, while the external redirect utilizes
    an HTTP 302 status code.

    :param location: The HTTP location to redirect to.
    :param internal: A boolean indicating whether the redirect should be
                     internal.
    :param code: The HTTP status code to use for the redirect. Defaults to 302.
    :param headers: Any HTTP headers to send with the response, as a
                    dictionary.
    '''

    if add_slash:
        if location is None:
            split_url = list(urlparse.urlsplit(state.request.url))
            new_proto = state.request.environ.get(
                'HTTP_X_FORWARDED_PROTO', split_url[0]
            )
            split_url[0] = new_proto
        else:
            split_url = urlparse.urlsplit(location)

        split_url[2] = split_url[2].rstrip('/') + '/'
        location = urlparse.urlunsplit(split_url)

    if not headers:
        headers = {}
    if internal:
        if code is not None:
            raise ValueError('Cannot specify a code for internal redirects')
        request.environ['pecan.recursive.context'] = request.context
        raise ForwardRequestException(location)
    if code is None:
        code = 302
    raise exc.status_map[code](location=location, headers=headers)


def render(template, namespace):
    '''
    Render the specified template using the Pecan rendering framework
    with the specified template namespace as a dictionary. Useful in a
    controller where you have no template specified in the ``@expose``.

    :param template: The path to your template, as you would specify in
                     ``@expose``.
    :param namespace: The namespace to use for rendering the template, as a
                      dictionary.
    '''

    return state.app.render(template, namespace)


def load_app(config):
    '''
    Used to load a ``Pecan`` application and its environment based on passed
    configuration.

    :param config: Can be a dictionary containing configuration, a string which
                    represents a (relative) configuration filename

    returns a pecan.Pecan object
    '''
    from .configuration import _runtime_conf, set_config
    set_config(config, overwrite=True)

    for package_name in getattr(_runtime_conf.app, 'modules', []):
        module = __import__(package_name, fromlist=['app'])
        if hasattr(module, 'app') and hasattr(module.app, 'setup_app'):
            app = module.app.setup_app(_runtime_conf)
            app.config = _runtime_conf
            return app
    raise RuntimeError(
        'No app.setup_app found in any of the configured app.modules'
    )


class Pecan(object):
    '''
    Base Pecan application object. Generally created using ``pecan.make_app``,
    rather than being created manually.

    Creates a Pecan application instance, which is a WSGI application.

    :param root: A string representing a root controller object (e.g.,
                "myapp.controller.root.RootController")
    :param default_renderer: The default template rendering engine to use.
                             Defaults to mako.
    :param template_path: A relative file system path (from the project root)
                          where template files live.  Defaults to 'templates'.
    :param hooks: A callable which returns a list of
                  :class:`pecan.hooks.PecanHook`
    :param custom_renderers: Custom renderer objects, as a dictionary keyed
                             by engine name.
    :param extra_template_vars: Any variables to inject into the template
                                namespace automatically.
    :param force_canonical: A boolean indicating if this project should
                            require canonical URLs.
    :param guess_content_type_from_ext: A boolean indicating if this project
                            should use the extension in the URL for guessing
                            the content type to return.
    '''

    SIMPLEST_CONTENT_TYPES = (
        ['text/html'],
        ['text/plain']
    )

    def __init__(self, root, default_renderer='mako',
                 template_path='templates', hooks=lambda: [],
                 custom_renderers={}, extra_template_vars={},
                 force_canonical=True, guess_content_type_from_ext=True, **kw):

        if isinstance(root, six.string_types):
            root = self.__translate_root__(root)

        self.root = root
        self.renderers = RendererFactory(custom_renderers, extra_template_vars)
        self.default_renderer = default_renderer

        # pre-sort these so we don't have to do it per-request
        if six.callable(hooks):
            hooks = hooks()

        self.hooks = list(sorted(
            hooks,
            key=operator.attrgetter('priority')
        ))
        self.template_path = template_path
        self.force_canonical = force_canonical
        self.guess_content_type_from_ext = guess_content_type_from_ext

    def __translate_root__(self, item):
        '''
        Creates a root controller instance from a string root, e.g.,

        > __translate_root__("myproject.controllers.RootController")
        myproject.controllers.RootController()

        :param item: The string to the item
        '''

        if '.' in item:
            parts = item.split('.')
            name = '.'.join(parts[:-1])
            fromlist = parts[-1:]

            module = __import__(name, fromlist=fromlist)
            kallable = getattr(module, parts[-1])
            msg = "%s does not represent a callable class or function."
            assert hasattr(kallable, '__call__'), msg % item
            return kallable()

        raise ImportError('No item named %s' % item)

    def route(self, req, node, path):
        '''
        Looks up a controller from a node based upon the specified path.

        :param node: The node, such as a root controller object.
        :param path: The path to look up on this node.
        '''

        path = path.split('/')[1:]
        try:
            node, remainder = lookup_controller(node, path)
            return node, remainder
        except NonCanonicalPath as e:
            if self.force_canonical and \
                    not _cfg(e.controller).get('accept_noncanonical', False):
                if req.method == 'POST':
                    raise RuntimeError(
                        "You have POSTed to a URL '%s' which "
                        "requires a slash. Most browsers will not maintain "
                        "POST data when redirected. Please update your code "
                        "to POST to '%s/' or set force_canonical to False" %
                        (req.pecan['routing_path'],
                            req.pecan['routing_path'])
                    )
                redirect(code=302, add_slash=True)
            return e.controller, e.remainder

    def determine_hooks(self, controller=None):
        '''
        Determines the hooks to be run, in which order.

        :param controller: If specified, includes hooks for a specific
                           controller.
        '''

        controller_hooks = []
        if controller:
            controller_hooks = _cfg(controller).get('hooks', [])
            if controller_hooks:
                return list(
                    sorted(
                        chain(controller_hooks, self.hooks),
                        key=operator.attrgetter('priority')
                    )
                )
        return self.hooks

    def handle_hooks(self, hook_type, *args):
        '''
        Processes hooks of the specified type.

        :param hook_type: The type of hook, including ``before``, ``after``,
                          ``on_error``, and ``on_route``.
        :param \*args: Arguments to pass to the hooks.
        '''
        if hook_type in ['before', 'on_route']:
            hooks = state.hooks
        else:
            hooks = reversed(state.hooks)

        for hook in hooks:
            result = getattr(hook, hook_type)(*args)
            # on_error hooks can choose to return a Response, which will
            # be used instead of the standard error pages.
            if hook_type == 'on_error' and isinstance(result, Response):
                return result

    def get_args(self, pecan_state, all_params, remainder, argspec, im_self):
        '''
        Determines the arguments for a controller based upon parameters
        passed the argument specification for the controller.
        '''
        args = []
        kwargs = dict()
        valid_args = argspec[0][1:]

        def _decode(x):
            return unquote_plus(x) if isinstance(x, six.string_types) \
                else x

        remainder = [_decode(x) for x in remainder]

        if im_self is not None:
            args.append(im_self)

        # grab the routing args from nested REST controllers
        if 'routing_args' in pecan_state:
            remainder = pecan_state['routing_args'] + list(remainder)
            del pecan_state['routing_args']

        # handle positional arguments
        if valid_args and remainder:
            args.extend(remainder[:len(valid_args)])
            remainder = remainder[len(valid_args):]
            valid_args = valid_args[len(args):]

        # handle wildcard arguments
        if [i for i in remainder if i]:
            if not argspec[1]:
                abort(404)
            args.extend(remainder)

        # get the default positional arguments
        if argspec[3]:
            defaults = dict(izip(argspec[0][-len(argspec[3]):], argspec[3]))
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
            for name, value in six.iteritems(all_params):
                if name not in argspec[0]:
                    kwargs[encode_if_needed(name)] = value

        return args, kwargs

    def render(self, template, namespace):
        renderer = self.renderers.get(
            self.default_renderer,
            self.template_path
        )
        if template == 'json':
            renderer = self.renderers.get('json', self.template_path)
        if ':' in template:
            renderer = self.renderers.get(
                template.split(':')[0],
                self.template_path
            )
            template = template.split(':')[1]
        return renderer.render(template, namespace)

    def handle_request(self, req, resp):
        '''
        The main request handler for Pecan applications.
        '''

        # get a sorted list of hooks, by priority (no controller hooks yet)
        state.hooks = self.hooks
        pecan_state = req.pecan

        # store the routing path for the current application to allow hooks to
        # modify it
        pecan_state['routing_path'] = path = req.encget('PATH_INFO')

        # handle "on_route" hooks
        self.handle_hooks('on_route', state)

        # lookup the controller, respecting content-type as requested
        # by the file extension on the URI
        pecan_state['extension'] = None

        # attempt to guess the content type based on the file extension
        if self.guess_content_type_from_ext \
                and not pecan_state['content_type'] \
                and '.' in path:
            new_path, extension = splitext(path)

            # preface with a letter to ensure compat for 2.5
            potential_type = guess_type('x' + extension)[0]

            if potential_type is not None:
                path = new_path
                pecan_state['extension'] = extension
                pecan_state['content_type'] = potential_type

        controller, remainder = self.route(req, self.root, path)
        cfg = _cfg(controller)

        if cfg.get('generic_handler'):
            raise exc.HTTPNotFound

        # handle generic controllers
        im_self = None
        if cfg.get('generic'):
            im_self = six.get_method_self(controller)
            handlers = cfg['generic_handlers']
            controller = handlers.get(req.method, handlers['DEFAULT'])
            handle_security(controller, im_self)
            cfg = _cfg(controller)

        # add the controller to the state so that hooks can use it
        state.controller = controller

        # if unsure ask the controller for the default content type
        content_types = cfg.get('content_types', {})
        if not pecan_state['content_type']:
            # attempt to find a best match based on accept headers (if they
            # exist)
            accept = getattr(req.accept, 'header_value', '*/*')
            if accept == '*/*' or (
                    accept.startswith('text/html,') and
                    list(content_types.keys()) in self.SIMPLEST_CONTENT_TYPES):
                pecan_state['content_type'] = cfg.get(
                    'content_type',
                    'text/html'
                )
            else:
                best_default = acceptparse.MIMEAccept(
                    accept
                ).best_match(
                    content_types.keys()
                )

                if best_default is None:
                    msg = "Controller '%s' defined does not support " + \
                          "content_type '%s'. Supported type(s): %s"
                    logger.error(
                        msg % (
                            controller.__name__,
                            pecan_state['content_type'],
                            content_types.keys()
                        )
                    )
                    raise exc.HTTPNotAcceptable()

                pecan_state['content_type'] = best_default
        elif cfg.get('content_type') is not None and \
                pecan_state['content_type'] not in content_types:

            msg = "Controller '%s' defined does not support content_type " + \
                  "'%s'. Supported type(s): %s"
            logger.error(
                msg % (
                    controller.__name__,
                    pecan_state['content_type'],
                    content_types.keys()
                )
            )
            raise exc.HTTPNotFound

        # get a sorted list of hooks, by priority
        state.hooks = self.determine_hooks(controller)

        # handle "before" hooks
        self.handle_hooks('before', state)

        # fetch any parameters
        if req.method == 'GET':
            params = dict(req.GET)
        else:
            params = dict(req.params)

        # fetch the arguments for the controller
        args, kwargs = self.get_args(
            pecan_state,
            params,
            remainder,
            cfg['argspec'],
            im_self
        )

        # get the result from the controller
        result = controller(*args, **kwargs)

        # a controller can return the response object which means they've taken
        # care of filling it out
        if result is response:
            return

        raw_namespace = result

        # pull the template out based upon content type and handle overrides
        template = content_types.get(pecan_state['content_type'])

        # check if for controller override of template
        template = pecan_state.get('override_template', template)
        pecan_state['content_type'] = pecan_state.get(
            'override_content_type',
            pecan_state['content_type']
        )

        # if there is a template, render it
        if template:
            if template == 'json':
                pecan_state['content_type'] = 'application/json'
            result = self.render(template, result)

        # If we are in a test request put the namespace where it can be
        # accessed directly
        if req.environ.get('paste.testing'):
            testing_variables = req.environ['paste.testing_variables']
            testing_variables['namespace'] = raw_namespace
            testing_variables['template_name'] = template
            testing_variables['controller_output'] = result

        # set the body content
        if isinstance(result, six.text_type):
            resp.text = result
        elif result:
            resp.body = result

        # set the content type
        if pecan_state['content_type']:
            resp.content_type = pecan_state['content_type']

    def __call__(self, environ, start_response):
        '''
        Implements the WSGI specification for Pecan applications, utilizing
        ``WebOb``.
        '''

        # create the request and response object
        state.request = req = Request(environ)
        state.response = resp = Response()
        state.hooks = []
        state.app = self
        state.controller = None

        # handle the request
        try:
            # add context and environment to the request
            req.context = environ.get('pecan.recursive.context', {})
            req.pecan = dict(content_type=None)

            self.handle_request(req, resp)
        except Exception as e:
            # if this is an HTTP Exception, set it as the response
            if isinstance(e, exc.HTTPException):
                state.response = e
                environ['pecan.original_exception'] = e

            # if this is not an internal redirect, run error hooks
            on_error_result = None
            if not isinstance(e, ForwardRequestException):
                on_error_result = self.handle_hooks('on_error', state, e)

            # if the on_error handler returned a Response, use it.
            if isinstance(on_error_result, Response):
                state.response = on_error_result
            else:
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
            del state.app
