:orphan:

#reload
Reloading Automatically as Files Change
---------------------------------------

Pausing to restart your development server as you work can be interruptive, so
:command:`pecan serve` provides a ``--reload`` flag to make life easier.

To provide this functionality, Pecan makes use of the Python
`watchdog <https://pypi.python.org/pypi/watchdog>`_ library.  You'll need to
install it for development use before continuing::

    $ pip install watchdog
    Downloading/unpacking watchdog
    ...
    Successfully installed watchdog

::

    $ pecan serve --reload config.py
    Monitoring for changes...
    Starting server in PID 000.
    serving on 0.0.0.0:8080, view at http://127.0.0.1:8080

As you work, Pecan will listen for any file or directory modification
events in your project and silently restart your server process in the
background.
