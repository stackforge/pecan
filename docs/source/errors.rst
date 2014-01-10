.. _errors:

Custom Error Documents
======================
In this article we will configure a Pecan application to display a custom
error page whenever the server returns a ``404 Page Not Found`` status.

This article assumes that you have already created a test application as
described in :ref:`quick_start`.

.. note::
    While this example focuses on the ``HTTP 404`` message, the same
    technique may be applied to define custom actions for any of the ``HTTP``
    status response codes in the 400 and 500 range. You are well advised to use
    this power judiciously.

.. _overview:

Overview
--------

Pecan makes it simple to customize error documents in two simple steps:

   * :ref:`configure`  of the HTTP status messages you want to handle
     in your application's ``config.py``
   * :ref:`controllers` to handle the status messages you have configured

.. _configure:

Configure Routing
-----------------
Let's configure our application ``test_project`` to route ``HTTP 404 Page 
Not Found`` messages to a custom controller.

First, let's update ``test_project/config.py`` to specify a new
error-handler.

::

    # Pecan Application Configurations
    app = {
        'root'            : 'test_project.controllers.root.RootController',
        'modules'         : ['test_project'],
        'static_root'     : '%(confdir)s/public', 
        'template_path'   : '%(confdir)s/test_project/templates',
        'reload'          : True,
        'debug'           : True,
        
        # modify the 'errors' key to direct HTTP status codes to a custom 
        # controller
        'errors'          : {
            #404           : '/error/404',
            404           : '/notfound',
            '__force_dict__' : True
        }
    }

Instead of the default error page, Pecan will now route 404 messages
to the controller method ``notfound``.

.. _controllers:

Write Custom Controllers
------------------------

The easiest way to implement the error handler is to 
add it to :class:`test_project.root.RootController` class
(typically in ``test_project/controllers/root.py``).

::
    
    from pecan import expose
    from webob.exc import status_map


    class RootController(object):

        @expose(generic=True, template='index.html')
        def index(self):
            return dict()

        @index.when(method='POST')
        def index_post(self, q):
            redirect('http://pecan.readthedocs.org/en/latest/search.html?q=%s' % q)


        ## custom handling of '404 Page Not Found' messages
        @expose('error.html')
        def notfound(self):
            return dict(status=404, message="test_project does not have this page")


        @expose('error.html')
        def error(self, status):
            try:
                status = int(status)
            except ValueError:
                status = 0
            message = getattr(status_map.get(status), 'explanation', '')
            return dict(status=status, message=message)


And that's it!

Notice that the only bit of code we added to our :class:`RootController` was::

        ## custom handling of '404 Page Not Found' messages
        @expose('error.html')
        def notfound(self):
            return dict(status=404, message="test_project does not have this page")

We simply :func:`~pecan.decorators.expose` the ``notfound`` controller with the
``error.html`` template (which was conveniently generated for us and placed
under ``test_project/templates/`` when we created ``test_project``).  As with
any Pecan controller, we return a dictionary of variables for interpolation by
the template renderer.

Now we can modify the error template, or write a brand new one to make the 404
error status page of ``test_project`` as pretty or fancy as we want.
