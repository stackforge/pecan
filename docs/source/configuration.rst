.. _configuration:

Configuring Pecan Applications
==============================
Pecan is very easy to configure. As long as you follow certain conventions,
using, setting and dealing with configuration should be very intuitive.  

Pecan configuration files are pure Python.

Default Values
---------------
Below is the complete list of default values the framework uses::


    server = {
        'port' : '8080',
        'host' : '0.0.0.0'
    }

    app = {
        'root' : None,
        'modules' : [],
        'static_root' : 'public', 
        'template_path' : ''
    }



.. _application_configuration:

Application Configuration
-------------------------
This is the part of the configuration that is specific to your application -
the framework uses it to wrap your application into a valid 
`WSGI app <http://www.wsgi.org/en/latest/what.html>`_.

A typical application configuration might look like this::

    app = {
        'root' : 'project.controllers.root.RootController',
        'modules' : ['project'],
        'static_root'   : '%(confdir)s/public', 
        'template_path' : '%(confdir)s/project/templates',
        'debug' : True 
    }

Let's look at each value and what it means:

**app** is a reserved variable name for the configuration, so make sure you
don't override it.

**root** The root controller of your application. Remember to provide
a string representing a Python path to some callable (e.g.,
``"yourapp.controllers.root.RootController"``).

**static_root** Points to the directory where your static files live (relative
to the project root).  By default, Pecan comes with middleware that can be
used to serve static files (like CSS and Javascript files) during development.

**template_path** Points to the directory where your template files live
(relative to the project root).

**debug** Enables ``WebError`` to display tracebacks in the browser 
(**IMPORTANT**: Make sure this is *always* set to ``False`` in production
environments).


.. _server_configuration:

Server Configuration
--------------------
Pecan provides some sane defaults.  Change these to alter the host and port your
WSGI app is served on::

    server = {
        'port' : '8080',
        'host' : '0.0.0.0'
    }

Additional Configuration
------------------------
Your application may need access to other configuration values at runtime 
(like third-party API credentials).  These types of configuration can be
defined in their own blocks in your configuration file::

    twitter = {
        'api_key' : 'FOO',
        'api_secret' : 'SECRET'
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


Dictionary Conversion
---------------------
In certain situations you might want to deal with keys and values, but in strict
dictionary form. The ``Config`` object has a helper method for this purpose
that will return a dictionary representation of itself, including nested values.

Below is a representation of how you can access the ``as_dict`` method and what
should return as a result (shortened for brevity):

::

    >>> from pecan import conf
    >>> conf
    Config({'app': Config({'errors': {}, 'template_path': '', 'static_root': 'public', [...]
    >>> conf.as_dict()
    {'app': {'errors': {}, 'template_path': '', 'static_root': 'public', [...]
    

Prefixing Dictionary Keys
-------------------------
``Config.as_dict`` allows you to pass an optional argument if you need to
prefix the keys in the returned dictionary. This is a single argument in string
form and it works like this (shortened for brevity):

::

    >>> from pecan import conf
    >>> conf
    Config({'app': Config({'errors': {}, 'template_path': '', 'static_root': 'public', [...]
    >>> conf.as_dict('prefixed_')
    {'prefixed_app': {'prefixed_errors': {}, 'prefixed_template_path': '', 'prefixed_static_root': 'prefixed_public', [...]
