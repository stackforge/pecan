.. _quick_start:

Creating Your First Pecan Application
=====================================

Let's create a small sample project with Pecan.

.. note::
    This guide does not cover the installation of Pecan. If you need
    instructions for installing Pecan, refer to :ref:`installation`.

.. _app_template:

Base Application Template
-------------------------

Pecan includes a basic template for starting a new project.  From your
shell, type::

    $ pecan create test_project

This example uses *test_project* as your project name, but you can replace
it with any valid Python package name you like.

Go ahead and change into your newly created project directory.::

    $ cd test_project

You'll want to deploy it in "development mode", such that it’s
available on :mod:`sys.path`, yet can still be edited directly from its
source distribution::

    $ python setup.py develop

Your new project contain these files::

    $ ls

    ├── MANIFEST.in
    ├── config.py
    ├── public
    │   ├── css
    │   │   └── style.css
    │   └── images
    ├── setup.cfg
    ├── setup.py
    └── test_project
        ├── __init__.py
        ├── app.py
        ├── controllers
        │   ├── __init__.py
        │   └── root.py
        ├── model
        │   └── __init__.py
        ├── templates
        │   ├── error.html
        │   ├── index.html
        │   └── layout.html
        └── tests
            ├── __init__.py
            ├── config.py
            ├── test_functional.py
            └── test_units.py

The number of files and directories may vary based on the version of
Pecan, but the above structure should give you an idea of what to
expect.

Let's review the files created by the template.

**public**
  All your static files (like CSS, Javascript, and images) live here.
  Pecan comes with a simple file server that serves these static files
  as you develop.

Pecan application structure generally follows the MVC_ pattern.  The
directories under ``test_project`` encompass your models, controllers
and templates.

.. _MVC: http://en.wikipedia.org/wiki/Model–view–controller

**test_project/controllers**
  The container directory for your controller files.
**test_project/templates**
  All your templates go in here.
**test_project/model**
  Container for your model files.

Finally, a directory to house unit and integration tests:

**test_project/tests**
  All of the tests for your application.

The ``test_project/app.py`` file controls how the Pecan application will be
created. This file must contain a :func:`setup_app` function which returns the
WSGI application object.  Generally you will not need to modify the ``app.py``
file provided by the base application template unless you need to customize
your app in a way that cannot be accomplished using config.  See
:ref:`python_based_config` below.

To avoid unneeded dependencies and to remain as flexible as possible,
Pecan doesn't impose any database or ORM (`Object Relational
Mapper`_).  If your project will interact with a database, you can add
code to ``model/__init__.py`` to load database bindings from your
configuration file and define tables and ORM definitions.

.. _Object Relational Mapper: http://en.wikipedia.org/wiki/Object-relational_mapping

.. _running_application:

Running the Application
-----------------------

The base project template creates the configuration file with the
basic settings you need to run your Pecan application in
``config.py``. This file includes the host and port to run the server
on, the location where your controllers and templates are stored on
disk, and the name of the directory containing any static files.

If you just run :command:`pecan serve`, passing ``config.py`` as the
configuration file, it will bring up the development server and serve
the app::

    $ pecan serve config.py 
    Starting server in PID 000.
    serving on 0.0.0.0:8080, view at http://127.0.0.1:8080

The location for the configuration file and the argument itself are very
flexible - you can pass an absolute or relative path to the file.

.. _python_based_config:

Python-Based Configuration
--------------------------
For ease of use, Pecan configuration files are pure Python--they're even saved
as ``.py`` files.

This is how your default (generated) configuration file should look::

    # Server Specific Configurations
    server = {
        'port': '8080',
        'host': '0.0.0.0'
    }

    # Pecan Application Configurations
    app = {
        'root': '${package}.controllers.root.RootController',
        'modules': ['${package}'],
        'static_root': '%(confdir)s/public', 
        'template_path': '%(confdir)s/${package}/templates',
        'debug': True,
        'errors': {
            '404': '/error/404',
            '__force_dict__': True
        }
    }

    logging = {
        'loggers': {
            'root' : {'level': 'INFO', 'handlers': ['console']},
            '${package}': {'level': 'DEBUG', 'handlers': ['console']}
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            }
        },
        'formatters': {
            'simple': {
                'format': ('%(asctime)s %(levelname)-5.5s [%(name)s]'
                           '[%(threadName)s] %(message)s')
            }
        }
    }

    # Custom Configurations must be in Python dictionary format::
    #
    # foo = {'bar':'baz'}
    #
    # All configurations are accessible at::
    # pecan.conf

You can also add your own configuration as Python dictionaries.

There's a lot to cover here, so we'll come back to configuration files in
a later chapter (:ref:`Configuration`).

    
The Application Root
--------------------

The **Root Controller** is the entry point for your application.  You
can think of it as being analogous to your application's root URL path
(in our case, ``http://localhost:8080/``).

This is how it looks in the project template
(``test_project.controllers.root.RootController``)::

    from pecan import expose
    from webob.exc import status_map


    class RootController(object):

        @expose(generic=True, template='index.html')
        def index(self):
            return dict()

        @index.when(method='POST')
        def index_post(self, q):
            redirect('http://pecan.readthedocs.org/en/latest/search.html?q=%s' % q)

        @expose('error.html')
        def error(self, status):
            try:
                status = int(status)
            except ValueError:
                status = 0
            message = getattr(status_map.get(status), 'explanation', '')
            return dict(status=status, message=message)


You can specify additional classes and methods if you need to do so, but for 
now, let's examine the sample project, controller by controller::

    @expose(generic=True, template='index.html')
    def index(self):
        return dict()

The :func:`index` method is marked as *publicly available* via the
:func:`~pecan.decorators.expose` decorator (which in turn uses the
``index.html`` template) at the root of the application
(http://127.0.0.1:8080/), so any HTTP ``GET`` that hits the root of your
application (``/``) will be routed to this method.

Notice that the :func:`index` method returns a Python dictionary. This dictionary
is used as a namespace to render the specified template (``index.html``) into
HTML, and is the primary mechanism by which data is passed from controller to 
template.

::

    @index.when(method='POST')
    def index_post(self, q):
        redirect('http://pecan.readthedocs.org/en/latest/search.html?q=%s' % q)

The :func:`index_post` method receives one HTTP ``POST`` argument (``q``).  Because
the argument ``method`` to :func:`@index.when` has been set to ``'POST'``, any
HTTP ``POST`` to the application root (in the example project, a form
submission) will be routed to this method.

::

    @expose('error.html')
    def error(self, status):
        try:
            status = int(status)
        except ValueError:
            status = 0
        message = getattr(status_map.get(status), 'explanation', '')
        return dict(status=status, message=message)

Finally, we have the :func:`error` method, which allows the application to display
custom pages for certain HTTP errors (``404``, etc...).

Running the Tests For Your Application
--------------------------------------

Your application comes with a few example tests that you can run, replace, and
add to.  To run them::

    $ python setup.py test -q
    running test
    running egg_info
    writing requirements to sam.egg-info/requires.txt
    writing sam.egg-info/PKG-INFO
    writing top-level names to sam.egg-info/top_level.txt
    writing dependency_links to sam.egg-info/dependency_links.txt
    reading manifest file 'sam.egg-info/SOURCES.txt'
    reading manifest template 'MANIFEST.in'
    writing manifest file 'sam.egg-info/SOURCES.txt'
    running build_ext
    ....
    ----------------------------------------------------------------------
    Ran 4 tests in 0.009s

    OK

The tests themselves can be found in the ``tests`` module in your project.

Deploying to a Web Server
-------------------------

Ready to deploy your new Pecan app?  Take a look at :ref:`deployment`.
