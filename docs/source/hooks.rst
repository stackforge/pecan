.. _hooks:

Hooks
=====
Pecan Hooks are a nice way to interact with the framework itself without having to
write WSGI middleware.

There is nothing wrong with WSGI Middleware, and actually, it is really easy to
use middleware with Pecan, but it can be hard (sometimes impossible) to have
access to Pecan's internals from within middleware.  Hooks make this easier.

Hooks allow you to execute code at key points throughout the life cycle of your request:

* ``on_route``: called before Pecan attempts to route a request to a controller

* ``before``: called after routing, but before controller code is run

* ``after``: called after controller code has been run

* ``on_error``: called when a request generates an exception

Implementation
--------------
In the below example, we will write a simple hook that will gather
some information about the request and print it to ``stdout``.

Your hook implementation needs to import ``PecanHook`` so it can be used as a base class.  
From there, you'll need to override the ``on_route``, ``before``, ``after``, or ``on_error`` methods::

    from pecan.hooks import PecanHook

    class SimpleHook(PecanHook):

        def before(self, state):
            print "\nabout to enter the controller..."

        def after(self, state):
            print "\nmethod: \t %s" % state.request.method
            print "\nresponse: \t %s" % state.response.status
            
``on_route``, ``before``, and ``after`` are each passed a shared state object which includes useful
information about the request, such as the request and response object, and which controller
was chosen by Pecan's routing.

``on_error`` is passed a shared state object **and** the original exception.
            
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
            print "DO SOMETHING!"
            return dict()

Now that our ``SimpleHook`` is included, let's see what happens when we run
the app and browse the application from our web browser::

    pecan serve config.py
    serving on 0.0.0.0:8080 view at http://127.0.0.1:8080

    about to enter the controller...
    DO SOMETHING!
    method: 	 GET
    response: 	 200 OK


