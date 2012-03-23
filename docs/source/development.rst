.. _development:

Developing Pecan Applications Locally
=====================================

Reloading Automatically as Files Change
---------------------------------------
.. include:: reload.rst

Debugging Pecan Applications
----------------------------
TODO

Serving Static Files
--------------------
Pecan comes with simple file serving middleware for serving CSS, Javascript,
images, and other static files.  You can configure it by ensuring that the 
following options are specified in your configuration file::

    app = {
        ...
        'debug': True,
        'static_root': '%(confdir)/public
    }

...where ``static_root`` is an absolute pathname to the directory in which your
static files live.  For convenience, the path may include the ``%(confdir)``
variable, which Pecan will substitute with the absolute path of your
configuration file at runtime.

.. note::
    In production, ``app.debug`` should *never* be set to ``True``, so you'll
    need to serve your static files via your production web server.
