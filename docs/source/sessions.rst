.. _session:

Working with Sessions and User Authentication
=============================================

Pecan provides no opinionated support for managing user sessions,
but it's easy to hook into your session framework of choice with minimal
effort.

This article details best practices for integrating the popular session
framework, `Beaker <http://beaker.groovie.org>`_, into your Pecan project.

Setting up Session Management
-----------------------------

There are several approaches that can be taken to set up session management.
One approach is WSGI middleware.  Another is Pecan :ref:`hooks`.

Here's an example of wrapping your WSGI application with Beaker's
:class:`~beaker.middleware.SessionMiddleware` in your project's ``app.py``.

::

    from pecan import conf, make_app
    from beaker.middleware import SessionMiddleware
    from test_project import model

    app = make_app(
        ...
    )
    app = SessionMiddleware(app, conf.beaker)

And a corresponding dictionary in your configuration file.

::

    beaker = {
        'session.key'           : 'sessionkey',
        'session.type'          : 'cookie',
        'session.validate_key'  : '05d2175d1090e31f42fa36e63b8d2aad',
        '__force_dict__'        : True
    }
