.. _quick_start:

Quick Start
===========

.. warning::
    This section is out of date. Please do not refer to it directly.

Here we will cover the basics for a small project in Pecan. More advanced
examples and methods are not covered here.

.. note::
    We will not cover how to get Pecan installed here. If you need installation
    details please go to :ref:`installation`


We include a basic template to have a good layout for a Pecan project. This is
accomplished by ``PasteScript`` so we need to invoke a command to create our
example project::

    $ pecan create -t base

The above command will prompt you for a project name. I chose *test_project*,
but you can also provided as an argument at the end of the example command
above.
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

    .
    ├── config.py
    ├── public
    │   ├── css
    │   │   └── style.css
    │   └── javascript
    │       └── shared.js
    ├── start.py
    └── test_project
        ├── __init__.py
        ├── controllers
        │   ├── __init__.py
        │   └── root.py
        ├── model
        │   ├── __init__.py
        └── templates
            ├── index.html
            ├── layout.html
            └── success.html

    7 directories, 11 files


A few things have been set for you, let's review them one by one:

*  **public**: All your public static files like CSS and Javascript are placed
  here. If you have some images (this example app doesn't) it would make sense
  to get them here as well.


Inside the project name you chose you have a couple of directories, and for the
most part, it will contain your models, controllers and templates:

*  **controllers**: The container directory for your controller files. 
*  **templates**: All your templates would go in here. 

To avoid unneeded dependencies and to remain as flexible as possible, Pecan doesn't impose any database or
ORM out of the box. You may notice that **model/__init__.py** is mostly empty. Its contents generally contain any code necessary define tables, ORM definitions, and parse bindings from ``pecan.conf``.


.. _running_application:

Running the application
-----------------------
There are 2 files that are important to start your application. In this case
``start.py`` and ``config.py`` are in charge of getting everything up and running.

If you just run ``start.py`` with Python, passing ``config`` as an argument for
configuration it will bring up the development server and serve the app::

    python start.py config
    Serving on http://0.0.0.0:8080
    serving on 0.0.0.0:8080 view at http://127.0.0.1:8080
    
To get up and running in no time the template helps a lot! 

.. note::
    If you fail to pass an argument you will get a small error message asking
    for a configuration file. Remember you need to pass the name of the
    configuration file without the ".py" extension. 


Simple Configuration
--------------------
We mentioned that you get a Python file with some configurations. The only
Python syntax that you will see is the first line that imports the
RootController that is in turn placed as the application root. Everything else,
including possible custom configurations are set as Python dictionaries.

This is how your default configuration file should look like::

    from test_project.controllers.root import RootController


    # Server Specific Configurations
    server = {
        'port' : '8080',
        'host' : '0.0.0.0'
    }

    # Pecan Application Configurations
    app = {
        'root' : RootController(),
        'static_root' : 'public', 
        'template_path' : 'test_project/templates',
        'debug' : True 
    }

    # Custom Configurations must be in Python dictionary format::
    #
    # foo = {'bar':'baz'}
    # 
    # All configurations are accessible at::
    # pecan.conf


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


    class SampleForm(Schema):
        name = v.String(not_empty=True)
        age = v.Int(not_empty=True)


    class RootController(object):
        @expose('index.html')
        def index(self, name='', age=''):
            return dict(errors=request.validation_error, name=name, age=age)
        
        @expose('success.html', schema=SampleForm(), error_handler='index')
        def handle_form(self, name, age):
            return dict(name=name, age=age)


Here you can specify other classes if you need to do so later on your project,
but for now we have an *index* method and a *handle_form* one.

**index**: Is *exposed* via the decorator ``@expose`` (that in turn uses the
``index.html`` file) as the root of the application, so anything that hits
'/' will touch this method.
Since we are doing some validation and want to pass any errors we might get to
the template, we set ``errors`` to receive anything that
``request.validation_error`` returns.
What your index method returns is dictionary that is received by the template
engine.


**handle_form**: It receives 2 parameters (*name* and *age*) that are validated
through the *SampleForm* schema class.
