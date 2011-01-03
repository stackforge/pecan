.. _hooks:

Hooks
=====
Pecan Hooks are a nice way to interact with the framework itself rather than
writing middleware.

There is nothing wrong with WSGI Middleware, and actually, it is really easy to
use middleware with Pecan, but it is rather hard (sometimes impossible) to have
access to Pecan's internals.

Hooks offer four ways of dealing with a request:

* ``on_route``: called before Pecan attempts to route a request

* ``before``: called after routing but before processing the request

* ``after``: called after a request has been processed

* ``on_error``: called when a request generates an error

Implementation
--------------
They are very easy to plug into Pecan. In the below example we will go through
a simple hook that will gather some information about the request and then it
will print it out to ``stdout``.

Your hook needs to import ``PecanHook`` which will be used to inherit from.

This is how your hook file should look like::

    from pecan.hooks import PecanHook

    class SimpleHook(PecanHook):

        def after(self, state):
            print "\nmethod: \t %s" % state.request.method
            print "response: \t %s" % state.response.status

The ``after`` method will be called after the request has been dealt with.

If you save your file as ``my_hook.py`` you should be able to add it to your 
application like this::

    from application.root import RootController
    from my_hook import SimpleHook

    app = make_app(
        RootController(),
        hooks           = [SimpleHook()]
        )

We are passing the ``RootController`` of our application (make sure to replace
the bogus values with your own) and our ``SimpleHook`` goes into a list for the
``hooks`` parameter.

We are not displaying how the entire file should look like but showing what is
of interest to get a hook into Pecan.

Running it
----------
Now that our ``SimpleHook`` is passed on, let's see what happens when we run
the app and browse the application::

    python start.py config
    Serving on http://0.0.0.0:8080
    serving on 0.0.0.0:8080 view at http://127.0.0.1:8080

    method: 	 GET
    response: 	 200 OK

``config`` is our configuration file that we pass on to ``start.py`` and as
soon as a request is served we see the information from our ``after`` method.


