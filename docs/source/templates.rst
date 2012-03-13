.. _templates:

Templating in Pecan 
===================

Pecan supports a variety of templating engines out of the box, and also provides
the ability to easily add support for new template engines. Currently, Pecan 
supports the following templating engines:

 * `Mako <http://www.makotemplates.org/>`_
 * `Genshi <http://genshi.edgewall.org/>`_
 * `Kajiki <http://kajiki.pythonisito.com/>`_
 * `Jinja2 <http://jinja.pocoo.org/>`_
 * `JSON`

The default template system is `mako`, but can be configured by passing the 
``default_renderer`` key in your app configuration::
    
    app = {
        'default_renderer' : 'kajiki',
        # ...
    }

The available renderer type strings are `mako`, `genshi`, `kajiki`, `jinja`, 
and `json`.


Using Renderers
---------------

:ref:`pecan_decorators` defines a decorator called ``@expose``, which is used
to flag a method as a controller. The ``@expose`` decorator takes a variety of
parameters, including a ``template`` argument, which is the path to the template
file to use for that controller. A controller will use the default template 
engine, unless the path is prefixed by another renderer name::

    class MyController(object):
        @expose('path/to/mako/template.html')
        def index(self):
            return dict(message='I am a mako template')

        @expose('kajiki:path/to/kajiki/template.html')
        def my_controller(self):
            return dict(message='I am a kajiki template')

For more information on the expose decorator, refer to :ref:`pecan_decorators`,
:ref:`pecan_core`, and :ref:`routing`.


Template Overrides and Manual Rendering
---------------------------------------

The :ref:`pecan_core` module contains two useful helper functions related to
templating. The first is ``override_template``, which allows you to overrides
which template is used in your controller, and the second is ``render``, which
allows you to manually render output using the Pecan templating framework.

To use ``override_template``, simply call it within the body of your controller

::

    class MyController(object):
        @expose('template_one.html')
        def index(self):
            # ...
            override_template('template_two.html')
            return dict(message='I will now render with template_two.html')

The ``render`` helper is also quite simple to use::

    @expose()
    def controller(self):
        return render('my_template.html', dict(message='I am the namespace'))


The JSON Renderer
-----------------

Pecan also provides a `JSON` renderer, e.g.,  ``@expose('json')``. For 
more information on using `JSON` in Pecan, please refer to :ref:`jsonify` and
:ref:`pecan_jsonify`.


Custom Renderers
----------------

To define a custom renderer, you can create a class that follows a simple
protocol::

    class MyRenderer(object):
        def __init__(self, path, extra_vars):
            '''
            Your renderer is provided with a path to templates,
            as configured by your application, and any extra 
            template variables, also as configured
            '''
            pass
    
        def render(self, template_path, namespace):
            '''
            Lookup the template based on the path, and render 
            your output based upon the supplied namespace 
            dictionary, as returned from the controller.
            '''
            return str(namespace)


To enable your custom renderer, you can define a ``custom_renderers`` key in
your application's configuration::

    app = {
        'custom_renderers' : {
            'my_renderer' : MyRenderer
        },
        # ...
    }
