.. _configuration:

Configuration
=============
Pecan is very easy to configured. As long as you follow certain conventions;
using, setting and dealing with configuration should be very intuitive.

Python files is what the framework uses to get the values from configuration
files. These files need to specify the values in a key/value way (Python
dictionaries).

Even if you want custom configuration values, you need to get them in the
configuration file as dictionaries.

No Configuration
----------------
What happens when no configuration is passed? Or if you are missing some values?
Pecan fills in anything that you might have left behind. This includes either
**app** or **server** completely and even if you left out specifics about them,
like the port number the server should be running on. 

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

