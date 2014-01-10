.. _templates:

Templating in Pecan 
===================

Pecan includes support for a variety of templating engines and also
makes it easy to add support for new template engines. Currently,
Pecan supports:

===============  =============
Template System  Renderer Name
===============  =============
 Mako_             mako
 Genshi_           genshi
 Kajiki_           kajiki
 Jinja2_           jinja
 JSON              json
===============  =============

.. _Mako: http://www.makotemplates.org/
.. _Genshi: http://genshi.edgewall.org/
.. _Kajiki: http://kajiki.pythonisito.com/
.. _Jinja2: http://jinja.pocoo.org/

The default template system is ``mako``, but that can be changed by
passing the ``default_renderer`` key in your application's
configuration::
    
    app = {
        'default_renderer' : 'kajiki',
        # ...
    }


Using Template Renderers
------------------------

:py:mod:`pecan.decorators` defines a decorator called
:func:`~pecan.decorators.expose`, which is used to flag a method as a public
controller. The :func:`~pecan.decorators.expose` decorator takes a ``template``
argument, which can be used to specify the path to the template file to use for
the controller method being exposed.

::

    class MyController(object):
        @expose('path/to/mako/template.html')
        def index(self):
            return dict(message='I am a mako template')

:func:`~pecan.decorators.expose` will use the default template engine unless
the path is prefixed by another renderer name.

::

        @expose('kajiki:path/to/kajiki/template.html')
        def my_controller(self):
            return dict(message='I am a kajiki template')

.. seealso::

  * :ref:`pecan_decorators`
  * :ref:`pecan_core`
  * :ref:`routing`


Overriding Templates
--------------------

:func:`~pecan.core.override_template` allows you to override the template set
for a controller method when it is exposed.  When
:func:`~pecan.core.override_template` is called within the body of the
controller method, it changes the template that will be used for that
invocation of the method.

::

    class MyController(object):
        @expose('template_one.html')
        def index(self):
            # ...
            override_template('template_two.html')
            return dict(message='I will now render with template_two.html')

Manual Rendering
----------------

:func:`~pecan.core.render` allows you to manually render output using the Pecan
templating framework. Pass the template path and values to go into the
template, and :func:`~pecan.core.render` returns the rendered output as text.

::

    @expose()
    def controller(self):
        return render('my_template.html', dict(message='I am the namespace'))


The JSON Renderer
-----------------

Pecan also provides a ``JSON`` renderer, which you can use by exposing
a controller method with ``@expose('json')``. 

.. seealso::

  * :ref:`jsonify`
  * :ref:`pecan_jsonify`


Defining Custom Renderers
-------------------------

To define a custom renderer, you can create a class that follows the
renderer protocol::

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


To enable your custom renderer, define a ``custom_renderers`` key in
your application's configuration::

    app = {
        'custom_renderers' : {
            'my_renderer' : MyRenderer
        },
        # ...
    }
