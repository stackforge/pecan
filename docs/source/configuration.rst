.. _configuration:

Configuring Pecan Applications
==============================

Pecan is very easy to configure. As long as you follow certain conventions,
using, setting and dealing with configuration should be very intuitive.  

Pecan configuration files are pure Python. Each "section" of the
configuration is a dictionary assigned to a variable name in the
configuration module.

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

The ``app`` configuration values are used by Pecan to wrap your
application into a valid `WSGI app
<http://www.wsgi.org/en/latest/what.html>`_. The ``app`` configuration
is specific to your application, and includes values like the root
controller class location.

A typical application configuration might look like this::

    app = {
        'root' : 'project.controllers.root.RootController',
        'modules' : ['project'],
        'static_root'   : '%(confdir)s/public', 
        'template_path' : '%(confdir)s/project/templates',
        'debug' : True 
    }

Let's look at each value and what it means:

**modules** 
  A list of modules where pecan will search for applications.
  Generally this should contain a single item, the name of your
  project's python package.  At least one of the listed modules must
  contain an ``app.setup_app`` function which is called to create the
  WSGI app.  In other words, this package should be where your
  ``app.py`` file is located, and this file should contain a
  ``setup_app`` function.

**root**
  The root controller of your application. Remember to provide a
  string representing a Python path to some callable (e.g.,
  ``"yourapp.controllers.root.RootController"``).

**static_root**
  The directory where your static files can be found (relative to
  the project root).  Pecan comes with middleware that can
  be used to serve static files (like CSS and Javascript files) during
  development.

**template_path**
  Points to the directory where your template files live (relative to
  the project root).

**debug**
  Enables the ability to display tracebacks in the browser and interactively
  debug during development.

.. warning::

  ``app`` is a reserved variable name for that section of the
  configuration, so make sure you don't override it.

.. warning::

  Make sure **debug** is *always* set to ``False`` in production environments.

.. seealso::

  * :ref:`app_template`


.. _server_configuration:

Server Configuration
--------------------

Pecan provides some sane defaults.  Change these to alter the host and port your
WSGI app is served on.

::

    server = {
        'port' : '8080',
        'host' : '0.0.0.0'
    }

Additional Configuration
------------------------

Your application may need access to other configuration values at
runtime (like third-party API credentials).  Put these settings in
their own blocks in your configuration file.

::

    twitter = {
        'api_key' : 'FOO',
        'api_secret' : 'SECRET'
    }

.. _accessibility:

Accessing Configuration at Runtime
----------------------------------

You can access any configuration value at runtime via :py:mod:`pecan.conf`.
This includes custom, application, and server-specific values.

For example, if you needed to specify a global administrator, you could
do so like this within the configuration file.

::

    administrator = 'foo_bar_user'

And it would be accessible in :py:mod:`pecan.conf` as::

    >>> from pecan import conf
    >>> conf.administrator
    'foo_bar_user'


Dictionary Conversion
---------------------

In certain situations you might want to deal with keys and values, but in strict
dictionary form. The :class:`~pecan.configuration.Config` object has a helper
method for this purpose that will return a dictionary representation of the
configuration, including nested values.

Below is a representation of how you can access the
:meth:`~pecan.configuration.Config.to_dict` method and what it returns as
a result (shortened for brevity):

::

    >>> from pecan import conf
    >>> conf
    Config({'app': Config({'errors': {}, 'template_path': '', 'static_root': 'public', [...]
    >>> conf.to_dict()
    {'app': {'errors': {}, 'template_path': '', 'static_root': 'public', [...]
    

Prefixing Dictionary Keys
-------------------------

:func:`~pecan.configuration.Config.to_dict` allows you to pass an optional
string argument if you need to prefix the keys in the returned dictionary.

::

    >>> from pecan import conf
    >>> conf
    Config({'app': Config({'errors': {}, 'template_path': '', 'static_root': 'public', [...]
    >>> conf.to_dict('prefixed_')
    {'prefixed_app': {'prefixed_errors': {}, 'prefixed_template_path': '', 'prefixed_static_root': 'prefixed_public', [...]


Dotted Keys and Native Dictionaries
-----------------------------------

Sometimes you want to specify a configuration option that includes dotted keys.
This is especially common when configuring Python logging.  By passing
a special key, ``__force_dict__``, individual configuration blocks can be
treated as native dictionaries.

::

    logging = {
        'loggers': {
            'root': {'level': 'INFO', 'handlers': ['console']},
            'sqlalchemy.engine': {'level': 'INFO', 'handlers': ['console']},
            '__force_dict__': True
        }
    }

    from myapp import conf
    assert isinstance(conf.logging.loggers, dict)
    assert isinstance(conf.logging.loggers['root'], dict)
    assert isinstance(conf.logging.loggers['sqlalchemy.engine'], dict)
