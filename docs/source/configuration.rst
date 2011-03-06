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

**root** Needs the Root Controller of your application, this where your main
class that points to all the spots in your application should be. Rememeber
that you are passing the actual object so you would need to import it at the
top of the file. In the example configuration, this would be something like::

    from myproject.controllers.root import RootController

**static_root** Points to the directory where your static files live in.

**template_path** The path where your templates are. 

**debug** Enables ``WebError`` to have full tracebacks in the browser (this is
OFF by default).

Any application specifics should go in here in the case that your environment
required it.


.. _server_configuration:

Server Configuration
--------------------
Depending on the WSGI server you choose, you will need some values. As shown
before, Pecan has already some defaults and they would look like this::

    server = {
        'port' : '8080',
        'host' : '0.0.0.0'
    }

There is not too much going on there, it is just specifying the port and the 
host it should use to serve the application. Any other values that you might
need can get added as key/values to that same dictionary so the server of your
choosing can use them.

.. _accessibility:

Accessibility 
--------------
You can access any configuration values at runtime importing ``conf`` from
``pecan``. This includes custom, application and server specific values.
Below is an example on how to access those values for an application::

    >>> from pecan import conf
    >>> conf.app.root
    <test_project.controllers.root.RootController object at 0x10292b0d0>
    >>> conf.app.static_root
    'public'
    >>> conf.app.template_path
    'test_project/templates'
    >>> conf.app.debug
    True



Custom and Single Values
------------------------
There might be times when you do not need to have a dictionary to specify some
values because all you need is a simple key that holds a value. For example, if
you needed to specify a global administrator, you could do so like this within
the configuration file::

    administrator = 'foo_bar_user'

And it would be accessible like this::

    >>>> from pecan import conf
    >>>> conf.administrator
    'foo_bar_user'

Similarly, if I had a custom ``foo`` entry on my configuration file once the 
app is running I can access ``foo`` values like::

    >>> from pecan import conf
    >>> conf.foo.bar
    True
    >>> conf.foo.baz
    False
    >>> conf.foo
    Config({'bar': True, 'baz': False})

