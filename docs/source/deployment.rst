.. _deployment:

Deploying Pecan in Production
=============================

Deploying a Pecan project to a production environment can be accomplished in
a variety of ways.  A few popular options for deployment are documented here.
It is important, however, to note that these examples are meant to provide
*direction*, not explicit instruction; deployment is usually heavily dependent
upon the needs and goals of individual applications, so your mileage may vary.

.. note::
    While Pecan comes packaged with a simple server *for development use* 
    (``pecan serve``), using a *production-ready* server similar to the ones
    described in this document is **very highly encouraged**.

Installing Pecan
----------------
For instructions on installing Pecan in most any environment, refer to
the documentation on :ref:`Installation`.

Disabling Debug Mode
--------------------
One of the most important steps to take before deploying a Pecan app into
production is to disable **Debug Mode**, which is responsible for serving
static files locally and providing a development-oriented debug environment
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

Generally speaking, the WSGI entry point to any Pecan application can be
generated using ``pecan.deploy``::

    from pecan.deploy import deploy
    application = deploy('/path/to/some/app/config.py')

Considerations for Static Files
-------------------------------
Pecan comes with simple static file serving (e.g., CSS, Javascript, images)
middleware which is **not** recommended for use in production.  

In production, Pecan doesn't serve media files itself; it leaves that job to
whichever web server you choose.

For serving static files in production, it's best to separate your concerns by
serving static files separately from your WSGI application (primarily for
performance reasons).  There are several popular ways to accomplish this.  Here
are two:

1.  Set up a proxy server (such as `nginx <http://nginx.org/>`_, `cherokee
    <http://www.cherokee-project.com>`_, or `lighttpd
    <http://www.lighttpd.net/>`_) to serve static files and proxy application
    requests through to your WSGI application:

::

    HTTP Client ─── Proxy Server (0.0.0.0:80) ─── Static Files
                       │
                       ├── WSGI Server Instance (127.0.0.1:5000)
                       ├── WSGI Server Instance (127.0.0.1:5001)
                       ├── WSGI Server Instance (127.0.0.1:5002)
                       └── WSGI Server Instance (127.0.0.1:5003)


2.  Serve static files via a separate service, virtual host, or CDN.

Common Recipes
--------------

Apache + mod_wsgi
+++++++++++++++++
`mod_wsgi <http://code.google.com/p/modwsgi/>`_ is a popular Apache module
which can be used to host any WSGI-compatible Python applicationa.

uwsgi + cherokee
++++++++++++++++
`uWSGI <http://projects.unbit.it/uwsgi/>`_ is a fast, self-healing and
developer/sysadmin-friendly application container server coded in pure C.  It
uses the `uwsgi <http://projects.unbit.it/uwsgi/wiki/uwsgiProtocol>`__
protocol, but can speak other protocols as well (http, fastcgi...).

Gunicorn + nginx
++++++++++++++++
`Gunicorn <http://gunicorn.org/'>`__, or "Green Unicorn", is a WSGI HTTP Server for
UNIX. It’s a pre-fork worker model ported from Ruby’s Unicorn project. It
supports both eventlet and greenlet. Running a Flask application on this server
is quite simple:
