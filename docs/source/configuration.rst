.. _configuration:

Configuration
=============
Pecan is very easy to configure. As long as you follow certain conventions;
using, setting and dealing with configuration should be very intuitive.

Python files is what the framework uses to get the values from configuration
files. These files need to specify the values in a key/value way (Python
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

A typical application configuration would look like this::

    app = {
        'root' : RootController(),
        'static_root' : 'public', 
        'template_path' : 'project/templates',
        'debug' : True 
    }

Let's look at each value and what it means:

**app** is a reserved variable name for the configuration, so make sure you are
not overriding, otherwise you will get default values.

**root** Needs the Root Controller of your application. Remember that you are
passing an object instance, so you'll need to import it at the top of the file.
In the example configuration, this would look something like::

    from myproject.controllers.root import RootController

**static_root** Points to the directory where your static files live.

**template_path** Points to the directory where your template files live.

**debug** Enables ``WebError`` to have full tracebacks in the browser (this is
OFF by default).


.. _server_configuration:

Server Configuration
--------------------
Pecan provides some defaults.  Change these to alter the host and port your
WSGI app is served on.::

    server = {
        'port' : '8080',
        'host' : '0.0.0.0'
    }

.. _accessibility:

Accessing Configuration at Runtime 
----------------------------------
You can access any configuration values at runtime via ``pecan.conf``.
This includes custom, application and server-specific values.
Below is an example on how to access those values from your application::


Custom and Single Values
------------------------
There might be times when you do not need a dictionary, but instead a simple
value. For example, if you needed to specify a global administrator, you could
do so like this within the configuration file::

    administrator = 'foo_bar_user'

And it would be accessible in `pecan.conf` like::

    >>>> from pecan import conf
    >>>> conf.administrator
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
