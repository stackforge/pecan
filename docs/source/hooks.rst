.. _hooks:

Pecan Hooks
===========

Although it is easy to use WSGI middleware with Pecan, it can be hard
(sometimes impossible) to have access to Pecan's internals from within
middleware.  Pecan Hooks are a way to interact with the framework,
without having to write separate middleware.

Hooks allow you to execute code at key points throughout the life cycle of your request:

* :func:`~pecan.hooks.PecanHook.on_route`: called before Pecan attempts to
  route a request to a controller

* :func:`~pecan.hooks.PecanHook.before`: called after routing, but before
  controller code is run

* :func:`~pecan.hooks.PecanHook.after`: called after controller code has been
  run

* :func:`~pecan.hooks.PecanHook.on_error`: called when a request generates an
  exception

Implementating a Pecan Hook
---------------------------

In the below example, a simple hook will gather some information about
the request and print it to ``stdout``.

Your hook implementation needs to import :class:`~pecan.hooks.PecanHook` so it
can be used as a base class.  From there, you'll want to override the
:func:`~pecan.hooks.PecanHook.on_route`, :func:`~pecan.hooks.PecanHook.before`,
:func:`~pecan.hooks.PecanHook.after`, or
:func:`~pecan.hooks.PecanHook.on_error` methods to
define behavior.

::

    from pecan.hooks import PecanHook

    class SimpleHook(PecanHook):

        def before(self, state):
            print "\nabout to enter the controller..."

        def after(self, state):
            print "\nmethod: \t %s" % state.request.method
            print "\nresponse: \t %s" % state.response.status
            
:func:`~pecan.hooks.PecanHook.on_route`, :func:`~pecan.hooks.PecanHook.before`,
and :func:`~pecan.hooks.PecanHook.after` are each passed a shared
state object which includes useful information, such as the request and
response objects, and which controller was selected by Pecan's routing::

    class SimpleHook(PecanHook):

        def on_route(self, state):
            print "\nabout to map the URL to a Python method (controller)..."
            assert state.controller is None  # Routing hasn't occurred yet
            assert isinstance(state.request, webob.Request)
            assert isinstance(state.response, webob.Response)
            assert isinstance(state.hooks, list)  # A list of hooks to apply

        def before(self, state):
            print "\nabout to enter the controller..."
            if state.request.path == '/':
                #
                # `state.controller` is a reference to the actual
                # `@pecan.expose()`-ed controller that will be routed to
                # and used to generate the response body
                #
                assert state.controller.__func__ is RootController.index.__func__
            assert isinstance(state.request, webob.Request)
            assert isinstance(state.response, webob.Response)
            assert isinstance(state.hooks, list)


:func:`~pecan.hooks.PecanHook.on_error` is passed a shared state object **and**
the original exception. If an :func:`~pecan.hooks.PecanHook.on_error` handler
returns a Response object, this response will be returned to the end user and
no furthur :func:`~pecan.hooks.PecanHook.on_error` hooks will be executed::

    class CustomErrorHook(PecanHook):

        def on_error(self, state, exc):
            if isinstance(exc, SomeExceptionType):
                return webob.Response('Custom Error!', status=500)

Attaching Hooks
---------------

Hooks can be attached in a project-wide manner by specifying a list of hooks
in your project's configuration file.

::

    app = {
        'root' : '...'
        # ...
        'hooks': lambda: [SimpleHook()]
    }

Hooks can also be applied selectively to controllers and their sub-controllers
using the :attr:`__hooks__` attribute on one or more controllers and
subclassing :class:`~pecan.hooks.HookController`.

::

    from pecan import expose
    from pecan.hooks import HookController
    from my_hooks import SimpleHook

    class SimpleController(HookController):
    
        __hooks__ = [SimpleHook()]
    
        @expose('json')
        def index(self):
            print "DO SOMETHING!"
            return dict()

Now that :class:`SimpleHook` is included, let's see what happens
when we run the app and browse the application from our web browser.

::

    pecan serve config.py
    serving on 0.0.0.0:8080 view at http://127.0.0.1:8080

    about to enter the controller...
    DO SOMETHING!
    method: 	 GET
    response: 	 200 OK


Hooks That Come with Pecan
--------------------------

Pecan includes some hooks in its core. This section will describe
their different uses, how to configure them, and examples of common
scenarios.

.. _requestviewerhook:

RequestViewerHook
'''''''''''''''''

This hook is useful for debugging purposes. It has access to every
attribute the ``response`` object has plus a few others that are specific to
the framework.

There are two main ways that this hook can provide information about a request:

#. Terminal or logging output (via an file-like stream like ``stdout``)
#. Custom header keys in the actual response.

By default, both outputs are enabled.

.. seealso::

  * :ref:`pecan_hooks`

Configuring RequestViewerHook
.............................

There are a few ways to get this hook properly configured and running. However,
it is useful to know that no actual configuration is needed to have it up and
running. 

By default it will output information about these items:

* path       : Displays the url that was used to generate this response
* status     : The response from the server (e.g. '200 OK')
* method     : The method for the request (e.g. 'GET', 'POST', 'PUT or 'DELETE')
* controller : The actual controller method in Pecan responsible for the response
* params     : A list of tuples for the params passed in at request time
* hooks      : Any hooks that are used in the app will be listed here.

The default configuration will show those values in the terminal via
``stdout`` and it will also add them to the response headers (in the
form of ``X-Pecan-item_name``).

This is how the terminal output might look for a `/favicon.ico` request::

    path         - /favicon.ico
    status       - 404 Not Found
    method       - GET
    controller   - The resource could not be found.
    params       - []
    hooks        - ['RequestViewerHook']

In the above case, the file was not found, and the information was printed to
`stdout`.  Additionally, the following headers would be present in the HTTP
response::

    X-Pecan-path	/favicon.ico
    X-Pecan-status	404 Not Found
    X-Pecan-method	GET
    X-Pecan-controller	The resource could not be found.
    X-Pecan-params	[]
    X-Pecan-hooks	['RequestViewerHook']

The configuration dictionary is flexible (none of the keys are required) and
can hold two keys: ``items`` and ``blacklist``.

This is how the hook would look if configured directly (shortened for brevity)::

    ...
    'hooks': lambda: [
        RequestViewerHook({'items':['path']})
    ]

Modifying Output Format
.......................

The ``items`` list specify the information that the hook will return.
Sometimes you will need a specific piece of information or a certain
bunch of them according to the development need so the defaults will
need to be changed and a list of items specified.

.. note::

    When specifying a list of items, this list overrides completely the
    defaults, so if a single item is listed, only that item will be returned by
    the hook.

The hook has access to every single attribute the request object has
and not only to the default ones that are displayed, so you can fine tune the
information displayed.

These is a list containing all the possible attributes the hook has access to
(directly from `webob`):

======================  ==========================
======================  ==========================
accept                       make_tempfile              
accept_charset               max_forwards               
accept_encoding              method                     
accept_language              params                     
application_url              path                       
as_string                    path_info                  
authorization                path_info_peek             
blank                        path_info_pop              
body                         path_qs                    
body_file                    path_url                     
body_file_raw                postvars                     
body_file_seekable           pragma                       
cache_control                query_string                 
call_application             queryvars                    
charset                      range                        
content_length               referer                      
content_type                 referrer                     
cookies                      relative_url                 
copy                         remote_addr                  
copy_body                    remote_user                  
copy_get                     remove_conditional_headers   
date                         request_body_tempfile_limit  
decode_param_names           scheme                       
environ                      script_name                  
from_file                    server_name                  
from_string                  server_port                  
get_response                 str_GET                      
headers                      str_POST                     
host                         str_cookies                  
host_url                     str_params                   
http_version                 str_postvars                 
if_match                     str_queryvars                
if_modified_since            unicode_errors               
if_none_match                upath_info                   
if_range                     url                          
if_unmodified_since          urlargs                      
is_body_readable             urlvars                      
is_body_seekable             uscript_name                 
is_xhr                       user_agent                   
make_body_seekable           
======================  ==========================

And these are the specific ones from Pecan and the hook:

 * controller
 * hooks 
 * params (params is actually available from `webob` but it is parsed 
   by the hook for redability)

Blacklisting Certain Paths
..........................

Sometimes it's annoying to get information about *every* single
request. To limit the ouptput, pass the list of URL paths for which
you do not want data as the ``blacklist``.

The matching is done at the start of the URL path, so be careful when using
this feature. For example, if you pass a configuration like this one::

    { 'blacklist': ['/f'] }

It would not show *any* url that starts with ``f``, effectively behaving like
a globbing regular expression (but not quite as powerful).

For any number of blocking you may need, just add as many items as wanted::

    { 'blacklist' : ['/favicon.ico', '/javascript', '/images'] }

Again, the ``blacklist`` key can be used along with the ``items`` key
or not (it is not required).
