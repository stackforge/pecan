.. _deployment:

Deploying Pecan in Production
=============================

Deploying a Pecan project to a production environment can be accomplished in
a variety of ways.  A few popular options for deployment are documented here.
It is important, however, to note that these examples are meant to provide
*direction*, not explicit instruction; deployment is usually heavily dependent
upon the needs and goals of individual applications, so your mileage will
probably vary.

.. note::
    While Pecan comes packaged with a simple server *for development use* 
    (``pecan serve``), using a *production-ready* server similar to the ones
    described in this document is **very highly encouraged**.

Installing Pecan
----------------
A few popular options are avaliable for installing Pecan in production
environments:

    *  Using `setuptools/distribute
       <http://packages.python.org/distribute/setuptools.html>`_.  Manage
       Pecan as a dependency in your project's ``setup.py`` file so that it's
       installed alongside your project (e.g., ``python
       /path/to/project/setup.py install``).  The default Pecan project
       described in :ref:`quick_start` facilitates this by including Pecan as
       a dependency for your project.

    *  Using `pip <http://www.pip-installer.org/en/latest/requirements.html>`_.
       Use ``pip freeze`` and ``pip install`` to create and install from
       a ``requirements.txt`` file for your project.

    *  Via the manual instructions found in :ref:`Installation`.

.. note::
    Regardless of the route you choose, it's highly recommended that all
    deployment installations be done in a Python `virtual environment
    <http://www.virtualenv.org/>`_.

Disabling Debug Mode
--------------------
One of the most important steps to take before deploying a Pecan app into
production is to disable **Debug Mode**, which is responsible for serving
static files locally and providing a development-oriented debugging environment
for tracebacks.  In your production configuration file, ensure that::

    # myapp/production_config.py
    app = {
        ...
        'debug': False
    }

Pecan and WSGI
--------------
WSGI is a Python standard that describes a standard interface between servers
and an application.  Any Pecan application is also known as a "WSGI
application" because it implements the WSGI interface, so any server that is
"WSGI compatible" may be used to serve your application.  A few popular
examples are:

* `mod_wsgi <http://code.google.com/p/modwsgi/>`__
* `uWSGI <http://projects.unbit.it/uwsgi/>`__
* `Gunicorn <http://gunicorn.org/>`__
* `waitress <http://docs.pylonsproject.org/projects/waitress/en/latest/>`__
* `CherryPy <http://cherrypy.org/>`__

Generally speaking, the WSGI entry point to any Pecan application can be
generated using ``pecan.deploy``::

    from pecan.deploy import deploy
    application = deploy('/path/to/some/app/config.py')

Considerations for Static Files
-------------------------------
Pecan comes with static file serving (e.g., CSS, Javascript, images)
middleware which is **not** recommended for use in production.  

In production, Pecan doesn't serve media files itself; it leaves that job to
whichever web server you choose.

For serving static files in production, it's best to separate your concerns by
serving static files separately from your WSGI application (primarily for
performance reasons).  There are several popular ways to accomplish this.  Here
are two:

1.  Set up a proxy server (such as `nginx <http://nginx.org/en>`__, `cherokee
    <http://www.cherokee-project.com>`__, or `lighttpd
    <http://www.lighttpd.net/>`__) to serve static files and proxy application
    requests through to your WSGI application:

::

    <HTTP Client> ─── <Production/Proxy Server>, e.g., Apache, nginx, cherokee (0.0.0.0:80) ─── <Static Files>
                       │
                       ├── <WSGI Server> Instance e.g., mod_wsgi, Gunicorn, uWSGI (127.0.0.1:5000 or /tmp/some.sock)
                       ├── <WSGI Server> Instance e.g., mod_wsgi, Gunicorn, uWSGI (127.0.0.1:5001 or /tmp/some.sock)
                       ├── <WSGI Server> Instance e.g., mod_wsgi, Gunicorn, uWSGI (127.0.0.1:5002 or /tmp/some.sock)
                       └── <WSGI Server> Instance e.g., mod_wsgi, Gunicorn, uWSGI (127.0.0.1:5003 or /tmp/some.sock)


2.  Serve static files via a separate service, virtual host, or CDN.

Common Recipes
--------------

Apache + mod_wsgi
+++++++++++++++++
`mod_wsgi <http://code.google.com/p/modwsgi/>`_ is a popular Apache module
which can be used to host any WSGI-compatible Python application (including your Pecan application).

To get started, check out the `installation and configuration documentation <http://code.google.com/p/modwsgi/wiki/InstallationInstructions>`_ for mod_wsgi.

For the sake of example, let's say that our project, ``simpleapp``, lives at
``/var/www/simpleapp``, and that a `virtualenv <http://www.virtualenv.org>`_
has been created at ``/var/www/venv`` with any necessary dependencies installed
(including Pecan).  Additionally, for security purposes, we've created a user,
``user1``, and a group, ``group1`` to execute our application under.

The first step is to create a ``.wsgi`` file which mod_wsgi will use as an entry point for your application::

    # /var/www/simpleapp/app.wsgi
    from pecan.deploy import deploy
    application = deploy('/var/www/simpleapp/config.py')

Next, add Apache configuration for your application.  Here's a simple example::

    <VirtualHost *>
        ServerName example.com

        WSGIDaemonProcess simpleapp user=user1 group=group1 threads=5 python-path=/var/www/venv/lib/python2.7/site-packages
        WSGIScriptAlias / /var/www/simpleapp/app.wsgi

        <Directory /var/www/simpleapp/>
            WSGIProcessGroup simpleapp
            WSGIApplicationGroup %{GLOBAL}
            Order deny,allow
            Allow from all
        </Directory>
    </VirtualHost>

For more instructions and examples of mounting WSGI applications using mod_wsgi, consult the `mod_wsgi Documentation <http://code.google.com/p/modwsgi/wiki/QuickConfigurationGuide#Mounting_The_WSGI_Application>`_.

Finally, restart Apache and give it a try.

uWSGI
+++++
`uWSGI <http://projects.unbit.it/uwsgi/>`_ is a fast, self-healing and
developer/sysadmin-friendly application container server coded in pure C.  It
uses the `uwsgi <http://projects.unbit.it/uwsgi/wiki/uwsgiProtocol>`__
protocol, but can speak other protocols as well (http, fastcgi...).

Running Pecan applications with uWSGI is a snap::

    $ pip install uwsgi
    $ pecan create simpleapp && cd simpleapp
    $ python setup.py develop

Next, let's create a new file in the project root::

    # wsgi.py
    from pecan.deploy import deploy
    application = deploy('config.py')

...and then run it with::

    $ uwsgi --http-socket 127.0.0.1:8000 -H /path/to/virtualenv -w wsgi

...or using a Unix socket (that nginx, for example, could be configured to
`proxy to <http://projects.unbit.it/uwsgi/wiki/RunOnNginx>`_)::

    $ uwsgi -s /tmp/uwsgi.sock -H ../path/to/virtualenv -w wsgi

Gunicorn
++++++++
`Gunicorn <http://gunicorn.org/>`__, or "Green Unicorn", is a WSGI HTTP Server for
UNIX. It’s a pre-fork worker model ported from Ruby’s Unicorn project. It
supports both eventlet and greenlet.

Running a Pecan application on Gunicorn is simple.  Let's walk through it with
Pecan's default project::

    $ pip install gunicorn
    $ pecan create simpleapp && cd simpleapp
    $ python setup.py develop
    $ gunicorn_pecan config.py
