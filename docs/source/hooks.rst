.. _hooks:

Hooks
=====
Pecan Hooks are a nice way to interact with the framework itself without having to
write WSGI middleware.

There is nothing wrong with WSGI Middleware, and actually, it is really easy to
use middleware with Pecan, but it can be hard (sometimes impossible) to have
access to Pecan's internals from within middleware.  Hooks make this easier.

Hooks offer four ways of dealing with a request:

* ``on_route``: called before Pecan attempts to route a request to a controller

* ``before``: called after routing, but before controller code is run

* ``after``: called after controller code has been run

* ``on_error``: called when a request generates an exception

Implementation
--------------
In the below example, we will write a simple hook that will gather
some information about the request and print it out to ``stdout``.

Your hook implementation needs to import ``PecanHook`` so it can be used as a base class::

    from pecan.hooks import PecanHook

    class SimpleHook(PecanHook):

        def after(self, state):
            print "\nmethod: \t %s" % state.request.method
            print "\nresponse: \t %s" % state.response.status
            
``on_route``, ``before``, and ``after`` are passed a shared state object which includes useful
information about the request, such as the request and response object, and which controller
was chosen by Pecan's routing.
            
Attaching Hooks
--------------
Hooks can be attached in a project-wide manner by specifying a list of hooks
in your project's ``app.py`` file::

    from application.root import RootController
    from my_hooks import SimpleHook
    
    app = make_app(
        RootController(),
        hooks = [SimpleHook()]
    )

Hooks can also be applied selectively to controllers and their sub-controllers
using the ``__hooks__`` attribute on one or more controllers::

    from pecan import expose
    from my_hooks import SimpleHook

    class SimpleController(object):
    
        __hooks__ = [SimpleHook()]
    
        @expose('json')
        def index(self):
            return dict()

Running it
----------
Now that our ``SimpleHook`` is included, let's see what happens when we run
the app and browse the application::

    pecan serve config.py
    serving on 0.0.0.0:8080 view at http://127.0.0.1:8080

    method: 	 GET
    response: 	 200 OK


