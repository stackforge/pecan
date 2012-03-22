.. _commands:

Command Line Pecan
==================
Any Pecan application can be controlled and inspected from the command line
using the built-in ``pecan`` command.  The usage examples of the ``pecan``
command in this document are intended to be invoked from your project's root
directory.  

Serving a Pecan App For Development
-----------------------------------
Pecan comes bundled with a lightweight WSGI development server based on
Python's ``wsgiref.simpleserver`` module.

Serving your Pecan app is as simple as invoking the ``pecan serve`` command::

    $ pecan serve config.py
    Starting server in PID 000.
    serving on 0.0.0.0:8080, view at http://127.0.0.1:8080

...and then visiting it in your browser.

The server ``host`` and ``port`` in your configuration file can be changed as
described in :ref:`server_configuration`.

Reloading Automatically as Files Change
+++++++++++++++++++++++++++++++++++++++

Pausing to restart your development server as you work can be interruptive, so
``pecan serve`` provides a ``--reload`` flag to make life easier.

To provide this functionality, Pecan makes use of the Python ``watchdog``
library.  You'll need to install it for development use before continuing::

    $ pip install watchdog
    Downloading/unpacking watchdog
    ...
    Successfully installed watchdog

::

    $ pecan serve --reload config.py
    Monitoring for changes...
    Starting server in PID 000.
    serving on 0.0.0.0:8080, view at http://127.0.0.1:8080

As you work, Pecan will listen for any file or directory modification events in your project and silently restart your server process in the background.


The Interactive Shell
---------------------
Pecan applications also come with an interactive Python shell which can be used
to execute expressions in an environment very similar to the one your
application runs in.  To invoke an interactive shell, use the ``pecan shell``
command::

    $ pecan shell config.py
    Pecan Interactive Shell
    Python 2.7.1 (r271:86832, Jul 31 2011, 19:30:53)
    [GCC 4.2.1 (Based on Apple Inc. build 5658)
    
      The following objects are available:
      wsgiapp    - This project's WSGI App instance
      conf       - The current configuration
      app        - webtest.TestApp wrapped around wsgiapp

    >>> conf
    Config({
        'app': Config({
            'root': 'myapp.controllers.root.RootController',
            'modules': ['myapp'],
            'static_root': '/Users/somebody/myapp/public', 
            'template_path': '/Users/somebody/myapp/project/templates',
            'errors': {'404': '/error/404'},
            'debug': True
        }),
        'server': Config({
            'host': '0.0.0.0',
            'port': '8080'
        })
    })
    >>> app
    <webtest.app.TestApp object at 0x101a830>
    >>> app.get('/')
    <200 OK text/html body='<html>\n ...\n\n'/936>

Press ``Ctrl-D`` to exit the interactive shell (or ``Ctrl-Z`` on Windows).

Using an Alternative Shell
++++++++++++++++++++++++++
``pecan shell`` has optional support for the `IPython <http://ipython.org/>`_
and `bpython <http://bpython-interpreter.org/>`_ alternative shells, each of
which can be specified with the ``--shell`` flag (or its abbreviated alias,
``-s``), e.g.,
::
    $ pecan shell --shell=ipython config.py
    $ pecan shell -s bpython config.py


Extending ``pecan`` with Custom Commands
----------------------------------------
TODO
