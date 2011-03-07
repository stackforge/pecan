.. _quick_start:

Quick Start
===========

Here we will cover the basics for a small project in Pecan. More advanced
examples and methods are not covered here.

.. note::
    We will not cover how to get Pecan installed here. If you need installation
    details please go to :ref:`installation` which includes the recommended way
    of setting up a proper development environment.


Base Application Template
-------------------------

We include a basic template to have a good layout for a Pecan project. This is
accomplished by  the ``pecan`` command line script bundled with the framework. 
Invoking the command to create a project is trivial::

    $ pecan create -t base

The above command will prompt you for a project name. I chose *test_project*,
but you can also provided as an argument at the end of the example command
above, like::

    $ pecan create -t base test_project

This is how it looks like when we run the whole command:: 

    $ pecan create -t base
    Selected and implied templates:
      pecan#pecan-base  Template for creating a basic Framework package

    Enter project name: test_project
    Variables:
      egg:      test_project
      package:  test_project
      project:  test_project
    Creating template pecan-base
    Creating directory ./test_project
      Recursing into +egg+
        Creating ./test_project/test_project/
        Copying __init__.py to ./test_project/test_project/__init__.py
        Recursing into controllers
          Creating ./test_project/test_project/controllers/
          Copying __init__.py to ./test_project/test_project/controllers/__init__.py
          Copying root.py to ./test_project/test_project/controllers/root.py
        Recursing into model
          Creating ./test_project/test_project/model/
          Copying __init__.py to ./test_project/test_project/model/__init__.py
        Recursing into templates
          Creating ./test_project/test_project/templates/
          Copying index.html to ./test_project/test_project/templates/index.html
          Copying layout.html to ./test_project/test_project/templates/layout.html
          Copying success.html to ./test_project/test_project/templates/success.html
      Recursing into public
        Creating ./test_project/public/
        Recursing into css
          Creating ./test_project/public/css/
          Copying style.css to ./test_project/public/css/style.css
        Recursing into javascript
          Creating ./test_project/public/javascript/
          Copying shared.js to ./test_project/public/javascript/shared.js
      Copying start.py_tmpl to ./test_project/start.py


This is how the structure of your new project should look like::

    ├── MANIFEST.in
    ├── config.py
    ├── public
    │   ├── css
    │   │   └── style.css
    │   └── javascript
    │       └── shared.js
    ├── setup.py
    ├── start.py
    ├── test_project
    │   ├── __init__.py
    │   ├── app.py
    │   ├── controllers
    │   │   ├── __init__.py
    │   │   └── root.py
    │   ├── model
    │   │   └── __init__.py
    │   ├── templates
    │   │   ├── error.html
    │   │   ├── index.html
    │   │   ├── layout.html
    │   │   └── success.html
    │   └── tests
    │       ├── __init__.py
    │       ├── test_config.py
    │       └── test_root.py
    └── test_project.egg-info
        ├── PKG-INFO
        ├── SOURCES.txt
        ├── dependency_links.txt
        ├── not-zip-safe
        ├── paster_plugins.txt
        ├── requires.txt
        └── top_level.txt

    9 directories, 25 files

The amount of files and directories may vary from time to time, but the above
structure should give you an idea of what you should expect.

A few things have been set for you, let's review them one by one:

*  **public**: All your public static files like CSS and Javascript are placed
  here. If you have some images (this example app doesn't) it would make sense
  to get them here as well.


Inside the project name you chose you have a few directories, and for the
most part, it will contain your models, controllers and templates:

*  **controllers**:  The container directory for your controller files.
*  **templates**:    All your templates would go in here.
*  **model**:        Container for your model files.
*  **tests**:        All your application test files.

To avoid unneeded dependencies and to remain as flexible as possible, Pecan doesn't impose any database or
ORM (Object Relational Mapper) out of the box. You may notice that **model/__init__.py** is mostly empty. 
Its contents generally contain any code necessary to define tables, ORM definitions, and parse bindings from 
your configuration file.


.. note::
    With your base project you also got some ready-to-run tests. Try running
    ``py.test`` (the recommended test runner for Pecan) and see them passing!


.. _running_application:

Running the application
-----------------------
The most important file to run your application is your configuration file, the
base project template should have created one for you already and it should be
named ``config.py``.

This file already contains the necessary information to run a Pecan app, like
ports, static paths and so forth. 

If you just run ``pecan serve`` passing ``config.py`` as an argument for
configuration it will bring up the development server and serve the app::

    $ pecan serve config.py 
    Starting subprocess with file monitor
    Starting server in PID 000.
    serving on 0.0.0.0:8080 view at http://127.0.0.1:8080

    
To get up and running in no time the template helps a lot! 

.. note::
    If you fail to pass an argument you will get a small error message asking
    for a configuration file. 

The location for the config file and the argument itself are very flexible. You
can pass an absolute path or just the name of the file without an extension,
like::

    $ pecan serve config


Simple Configuration
--------------------
We mentioned that you get a Python file with some configurations. The only
Python syntax that you will see is the first line that imports the
RootController that is in turn placed as the application root. Everything else,
including possible custom configurations are set as Python dictionaries.

This is how your default configuration file should look like::

    from test_project.controllers.root import RootController

    import test_project

    # Server Specific Configurations
    server = {
        'port' : '8080',
        'host' : '0.0.0.0'
    }

    # Pecan Application Configurations
    app = {
        'root' : RootController(),
        'modules' : [test_project],
        'static_root' : 'public', 
        'template_path' : 'test_project/templates',
        'reload': True,
        'debug' : True,
        'errors' : {
            '404' : '/error/404',
            '__force_dict__' : True
        }
    }

    # Custom Configurations must be in Python dictionary format::
    #
    # foo = {'bar':'baz'}
    # 
    # All configurations are accessible at::
    # pecan.conf


.. note::
    If you named your project something other than *test_project* 
    you should see that same name above instead.


**Nothing** in the configuration file above is actually required for Pecan to
be able to run. If you fail to provide some values Pecan will fill in the
missing things it needs to run.

You also get the ability to set your own configurations as dictionaries and you
get a commented out example on how to do that.

We are not going to explain much more about configuration here, if you need
more specific details, go to the :ref:`Configuration` section.

    
Root Controller
---------------
The Root Controller is the main point of contact between your application and
the framework.

This is how it looks from the project template::

    from pecan import expose, request
    from formencode import Schema, validators as v
    from webob.exc import status_map


    class SampleForm(Schema):
        name = v.String(not_empty=True)
        age = v.Int(not_empty=True)


    class RootController(object):
        @expose('index.html')
        def index(self, name='', age=''):
            return dict(errors=request.validation_errors, name=name, age=age)
        
        @expose('success.html', schema=SampleForm(), error_handler='index')
        def handle_form(self, name, age):
            return dict(name=name, age=age)
        
        @expose('error.html')
        def error(self, status):
            try:
                status = int(status)
            except ValueError:
                status = 0
            message = getattr(status_map.get(status), 'explanation', '')
            return dict(status=status, message=message)



Here you can specify other classes if you need to do so later on your project,
but for now we have an *index* method and a *handle_form* one.

**index**: Is *exposed* via the decorator ``@expose`` (that in turn uses the
``index.html`` file) as the root of the application, so anything that hits
the root of you application will touch this method.

What your index method returns is a dictionary that is received by the template
engine and translated into valid HTML.

Since we are doing some validation and want to pass any errors we might get to
the template, we set ``errors`` to receive anything that
``request.validation_errors`` returns.


**handle_form**: It receives 2 arguments (*name* and *age*) that are validated
through the *SampleForm* schema class.

The ``error_handler`` has been set to index, this means that when errors are raised 
they will be sent to the index controller so it returns them to the template.

**error**: Finally, we have the error controller that allows you application to 
custom display any possible errors that you might want to display. 

Application Interaction
-----------------------
If you still have your application running and you visit your browser, you should
see a nice page with some information about Pecan and a form so you can play a bit 
with.

This is very basic but it will give you the grounds necessary to build your application
and understand some of the features the framework packs.
