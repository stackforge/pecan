.. _configuration:

Configuration
=============
Pecan is very easy to configure. As long as you follow certain conventions,
using, setting and dealing with configuration should be very intuitive.

Pecan configuration files are pure Python.  These files need to specify the values in a key/value way (Python
dictionaries) or if you need simple one-way values you can also specify them as
direct variables (more on that below).

Even if you want custom configuration values, you need to get them in the
configuration file as dictionaries.

No Configuration
----------------
What happens when no configuration is passed? Or if you are missing some values?
Pecan fills in anything that you might have left behind, like specific values or  
even if you leave them out completely. This includes
**app** and **server** but will not, however, include any custom configurations.

Defaults
--------
Below is the complete default values the framework uses::


    server = {
        'port' : '8080',
        'host' : '0.0.0.0'
    }

    app = {
        'root' : None,
        'static_root' : 'public', 
        'template_path' : '',
        'debug' : False
    }



.. _application_configuration:

Application Configuration
-------------------------
This is the part of the configuration that is specific to your application.
Things like debug mode, Root Controller and possible Hooks, should be specified
here. This is what is used when the framework is wrapping your application into
a valid WSGI app.

A typical application configuration might look like this::

    app = {
        'root' : 'project.controllers.root.RootController',
        'modules' : ['project'],
        'static_root'   : '%(confdir)s/public', 
        'template_path' : '%(confdir)s/project/templates',
        'reload' : True,
        'debug' : True 
    }

Let's look at each value and what it means:

**app** is a reserved variable name for the configuration, so make sure you are
not overriding, otherwise you will get default values.

**root** The root controller of your application. Remember to provide
a string representing a Python path to some callable (e.g.,
`yourapp.controllers.root.RootController`).

**static_root** Points to the directory where your static files live (relative
to the project root).

**template_path** Points to the directory where your template files live
(relative to the project root).

**reload** - When ``True``, ``pecan serve`` will listen for file changes and
restare your app (especially useful for development).

**debug** Enables ``WebError`` to have display tracebacks in the browser 
(**IMPORTANT**: Make sure this is *always* set to ``False`` in production
environments).


.. _server_configuration:

Server Configuration
--------------------
Pecan provides some defaults.  Change these to alter the host and port your
WSGI app is served on::

    server = {
        'port' : '8080',
        'host' : '0.0.0.0'
    }

.. _accessibility:

Accessing Configuration at Runtime 
----------------------------------
You can access any configuration value at runtime via ``pecan.conf``.
This includes custom, application and server-specific values.

For example, if you needed to specify a global administrator, you could
do so like this within the configuration file::

    administrator = 'foo_bar_user'

And it would be accessible in `pecan.conf` as::

    >>> from pecan import conf
    >>> conf.administrator
    'foo_bar_user'


Fully Valid Dictionaries
------------------------
In certain situations you might want to deal with keys and values, but in strict
dictionary form. The ``Config`` object has a helper method for this purpose
that will return a dictionary representation of itself including nested values.

Below is a representation of how you can access the ``as_dict`` method and what
should return as a result (shortened for brevity):

::

    >>> from pecan import conf
    >>> conf
    Config({'app': Config({'errors': {}, 'template_path': '', 'static_root': 'public', [...]
    >>> conf.as_dict()
    {'app': {'errors': {}, 'template_path': '', 'static_root': 'public', [...]
    

Prefixing Values
----------------
``Config.as_dict`` allows you to pass an optional argument if you need to
prefix the keys in the returned dictionary. This is a single argument in string
form and it works like this (shortened for brevity):

::

    >>> from pecan import conf
    >>> conf
    Config({'app': Config({'errors': {}, 'template_path': '', 'static_root': 'public', [...]
    >>> conf.as_dict('prefixed_')
    {'prefixed_app': {'prefixed_errors': {}, 'prefixed_template_path': '', 'prefixed_static_root': 'prefixed_public', [...]
