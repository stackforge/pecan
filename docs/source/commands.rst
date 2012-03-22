.. _commands:

Command Line Pecan
==================
Any Pecan application can be controlled and inspected from the command line
using the built-in ``pecan`` command.

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
TODO
