.. Pecan documentation master file, created by
   sphinx-quickstart on Sat Oct  9 14:41:27 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pecan's documentation
=========================

A WSGI object-dispatching web framework, in the spirit of TurboGears, only 
much much smaller, with many fewer dependencies.


Contents:

.. toctree::
   :maxdepth: 2

   quick_start.rst 
   routing.rst 
   configuration.rst 
   templates.rst 
   hooks.rst 
   jsonify.rst 
   secure_controller.rst 
   validation_n_errors.rst
   app_engine.rst


Introduction
============
A WSGI object-dispatching lean web framework, in the spirit of TurboGears, only 
much much smaller, with many fewer dependencies. 

 * Object-Dispatch for easy routing
 * Pre and Post Hooks 
 * REST capabilities 
 * Validation and Error handling
 * Secure controllers
 * Template language support
 * AppEngine out of the box (no patching!)



Pecan Hello World
------------------
In this example we use ``httpserver`` from ``paste`` but feel free to use any 
WSGI server you want::

    from paste import httpserver
    from pecan import make_app, expose


    class RootController(object):

        @expose()
        def index(self):
            return 'Hello, World!'

    app = make_app(RootController(), debug=True)
    httpserver.serve(app, host='0.0.0.0', port=8080)





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

