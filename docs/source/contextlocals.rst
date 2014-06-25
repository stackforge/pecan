.. _contextlocals:


Context/Thread-Locals vs. Explicit Argument Passing
===================================================
In any pecan application, the module-level ``pecan.request`` and
``pecan.response`` are proxy objects that always refer to the request and
response being handled in the current thread.

This `thread locality` ensures that you can safely access a global reference to
the current request and response in a multi-threaded environment without
constantly having to pass object references around in your code; it's a feature
of pecan that makes writing traditional web applications easier and less
verbose.

Some people feel thread-locals are too implicit or magical, and that explicit
reference passing is much clearer and more maintainable in the long run.
Additionally, the default implementation provided by pecan uses
:func:`threading.local` to associate these context-local proxy objects with the
`thread identifier` of the current server thread.  In asynchronous server
models - where lots of tasks run for short amounts of time on
a `single` shared thread - supporting this mechanism involves monkeypatching
:func:`threading.local` to behave in a greenlet-local manner.

Disabling Thread-Local Proxies
------------------------------

If you're certain that you `do not` want to utilize context/thread-locals in
your project, you can do so by passing the argument
``use_context_locals=False`` in your application's configuration file::

    app = {
        'root': 'project.controllers.root.RootController',
        'modules': ['project'],
        'static_root': '%(confdir)s/public',
        'template_path': '%(confdir)s/project/templates',
        'debug': True,
        'use_context_locals': False
    }

Additionally, you'll need to update **all** of your pecan controllers to accept
positional arguments for the current request and response::

    class RootController(object):

        @pecan.expose('json')
        def index(self, req, resp):
            return dict(method=req.method) # path: /

        @pecan.expose()
        def greet(self, req, resp, name):
            return name  # path: /greet/joe

It is *imperative* that the request and response arguments come **after**
``self`` and before any positional form arguments.
