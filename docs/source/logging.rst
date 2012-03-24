.. |FileHandler| replace:: ``FileHandler``
.. _FileHandler: http://docs.python.org/dev/library/logging.handlers.html#filehandler

.. |RotatingFileHandler| replace:: ``RotatingFileHandler``
.. _RotatingFileHandler: http://docs.python.org/dev/library/logging.handlers.html#rotatingfilehandler

.. |SysLogHandler| replace:: ``SysLogHandler``
.. _SysLogHandler: http://docs.python.org/dev/library/logging.handlers.html#sysloghandler

.. |SMTPHandler| replace:: ``SMTPHandler``
.. _SMTPHandler: http://docs.python.org/dev/library/logging.handlers.html#smtphandler

.. _logging:

Logging
=======
Pecan hooks into the Python standard library's ``logging`` module by passing
logging configuration options into the
`logging.config.dictConfig
<http://docs.python.org/library/logging.config.html#configuration-dictionary-schema>`_
function.  The full documentation for the `dictConfig
<http://docs.python.org/library/logging.config.html#configuration-dictionary-schema>`_
format is the best source of information for logging configuration, but to get
you started, this chapter will provide you with a few simple examples.

Configuring Logging
-------------------
Sample logging configuration is provided with the quickstart project
introduced in :ref:`quick_start`::

    $ pecan create myapp

::

    # myapp/config.py

    app = { ... }
    server = { ... }

    logging = {
        'loggers': {
            'root' : {'level': 'INFO', 'handlers': ['console']},
            'myapp': {'level': 'DEBUG', 'handlers': ['console']}
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

This configuration defines one handler:

* ``console`` logs messages to ``stderr`` using the ``simple`` formatter.

...and two loggers.

* ``myapp`` logs messages sent at a level above or equal to ``DEBUG`` to
  the ``console`` handler

* ``root`` logs messages at a level above or equal to the ``INFO`` level to
  the ``console`` handler


Writing Logs in Your Application
--------------------------------
The logger named ``myapp`` is reserved for your usage in your Pecan
application.

Once you have configured your logging, you can place logging calls in your
code.  Using the logging framework is very simple.  Here’s an example::

    # myapp/myapp/controllers/root.py
    from pecan import expose

    logger = logging.getLogger(__name__)

    class RootController(object):

        @expose()
        def index(self):
            if bad_stuff():
                logger.error('Uh-oh!')
            return dict()

Writing Logs to Files and Other Locations
-----------------------------------------
Python's ``logging`` library defines a variety of handlers that assist in
writing logs to file.  A few interesting ones are:

* |FileHandler|_ - used to log messages to a file on the filesystem
* |RotatingFileHandler|_ - similar to |FileHandler|_, but also rotates logs
  periodically
* |SysLogHandler|_ - used to log messages to a UNIX syslog
* |SMTPHandler|_ - used to log messages to an email address via SMTP

Using any of them is as simple as defining a new handler in your
application's ``logging`` block and assigning it to one of more loggers.

Logging Requests with Paste Translogger
---------------------------------------
`Paste <http://pythonpaste.org/>`_ (which is not included with Pecan) includes
the `TransLogger <http://pythonpaste.org/modules/translogger.html>`_ middleware
for logging requests in `Apache Combined Log Format
<http://httpd.apache.org/docs/2.2/logs.html#combined>`_. Combined with
file-based logging, TransLogger can be used to create an ``access.log`` file
similar to ``Apache``.

To add this middleware, modify your the ``setup_app`` method in your
project's ``app.py`` as follows::

    # myapp/myapp/app.py
    from pecan import make_app
    from paste.translogger import TransLogger

    def setup_app(config):
        # ...
        app = make_app(
            config.app.root
            # ...
        )
        app = TransLogger(app, setup_console_handler=False)
        return app

By default, ``TransLogger`` creates a logger named ``wsgi``, so you'll need to
specify a new (file-based) handler for this logger in our Pecan configuration
file::

    # myapp/config.py

    app = { ... }
    server = { ... }

    logging = {
        'loggers': {
            # ...
            'wsgi': {'level': 'INFO', 'handlers': ['logfile'], 'qualname': 'wsgi'}
        },
        'handlers': {
            # ...
            'logfile': {
                'class': 'logging.FileHandler',
                'filename': '/etc/access.log',
                'level': 'INFO',
                'formatter': 'messageonly'
            }
        },
        'formatters': {
            # ...
            'messageonly': {'format': '%(message)s'}
        }
    }
