.. _databases:

Working with Databases, Transactions, and ORM's
===============================================

Pecan provides no opinionated support for working with databases, but
it's easy to hook into your ORM of choice.  This article details best
practices for integrating the popular Python ORM, SQLAlchemy_, into
your Pecan project.

.. _SQLAlchemy: http://sqlalchemy.org

``init_model`` and Preparing Your Model
---------------------------------------

Pecan's default quickstart project includes an empty stub directory
for implementing your model as you see fit.

::

    .
    └── test_project
        ├── app.py
        ├── __init__.py
        ├── controllers
        ├── model
        │   ├── __init__.py
        └── templates
    
By default, this module contains a special method, :func:`init_model`.

::

    from pecan import conf

    def init_model():
        """
        This is a stub method which is called at application startup time.
        
        If you need to bind to a parse database configuration, set up tables or
        ORM classes, or perform any database initialization, this is the 
        recommended place to do it.

        For more information working with databases, and some common recipes,
        see http://pecan.readthedocs.org/en/latest/databases.html
        """
        pass
        
The purpose of this method is to determine bindings from your
configuration file and create necessary engines, pools,
etc. according to your ORM or database toolkit of choice.

Additionally, your project's :py:mod:`model` module can be used to define
functions for common binding operations, such as starting
transactions, committing or rolling back work, and clearing a session.
This is also the location in your project where object and relation
definitions should be defined.  Here's what a sample Pecan
configuration file with database bindings might look like.

::

    # Server Specific Configurations
    server = {
        ...
    }
    
    # Pecan Application Configurations
    app = {
        ...
    }
    
    # Bindings and options to pass to SQLAlchemy's ``create_engine``
    sqlalchemy = {
        'url'           : 'mysql://root:@localhost/dbname?charset=utf8&use_unicode=0',
        'echo'          : False,
        'echo_pool'     : False,
        'pool_recycle'  : 3600,
        'encoding'      : 'utf-8'
    }

And a basic model implementation that can be used to configure and
bind using SQLAlchemy.

::

    from pecan                  import conf
    from sqlalchemy             import create_engine, MetaData
    from sqlalchemy.orm         import scoped_session, sessionmaker
    
    Session = scoped_session(sessionmaker())
    metadata = MetaData()
    
    def _engine_from_config(configuration):
        configuration = dict(configuration)
        url = configuration.pop('url')
        return create_engine(url, **configuration)
    
    def init_model():
        conf.sqlalchemy.engine = _engine_from_config(conf.sqlalchemy)
    
    def start():
        Session.bind = conf.sqlalchemy.engine
        metadata.bind = Session.bind
    
    def commit():
        Session.commit()
    
    def rollback():
        Session.rollback()
    
    def clear():
        Session.remove()
        
Binding Within the Application
------------------------------

There are several approaches to wrapping your application's requests
with calls to appropriate model function calls.  One approach is WSGI
middleware.  We also recommend Pecan :ref:`hooks`.  Pecan comes with
:class:`~pecan.hooks.TransactionHook`, a hook which can be used to wrap
requests in database transactions for you.  To use it, simply include it in
your project's ``app.py`` file and pass it a set of functions related to
database binding.

::

    from pecan import conf, make_app
    from pecan.hooks import TransactionHook
    from test_project import model

    app = make_app(
        conf.app.root,
        static_root     = conf.app.static_root,
        template_path   = conf.app.template_path,
        debug           = conf.app.debug,
        hooks           = [
            TransactionHook(
                model.start,
                model.start_read_only,
                model.commit,
                model.rollback,
                model.clear
            )
        ]
    )
    
In the above example, on HTTP ``POST``, ``PUT``, and ``DELETE``
requests, :class:`~pecan.hooks.TransactionHook` takes care of the transaction
automatically by following these rules:

#.  Before controller routing has been determined, :func:`model.start`
    is called.  This function should bind to the appropriate
    SQLAlchemy engine and start a transaction.

#.  Controller code is run and returns.

#.  If your controller or template rendering fails and raises an
    exception, :func:`model.rollback` is called and the original
    exception is re-raised.  This allows you to rollback your database
    transaction to avoid committing work when exceptions occur in your
    application code.

#.  If the controller returns successfully, :func:`model.commit` and
    :func:`model.clear` are called.
    
On idempotent operations (like HTTP ``GET`` and ``HEAD`` requests),
:class:`~pecan.hooks.TransactionHook` handles transactions following different
rules.

#.  ``model.start_read_only()`` is called.  This function should bind
    to your SQLAlchemy engine.

#.  Controller code is run and returns.

#.  If the controller returns successfully, ``model.clear()`` is
    called.

Also note that there is a useful :func:`~pecan.decorators.after_commit`
decorator provided in :ref:`pecan_decorators`.

Splitting Reads and Writes
--------------------------

Employing the strategy above with :class:`~pecan.hooks.TransactionHook` makes
it very simple to split database reads and writes based upon HTTP methods
(i.e., GET/HEAD requests are read-only and would potentially be routed
to a read-only database slave, while POST/PUT/DELETE requests require
writing, and would always bind to a master database with read/write
privileges).  It's also possible to extend
:class:`~pecan.hooks.TransactionHook` or write your own hook implementation for
more refined control over where and when database bindings are called.
