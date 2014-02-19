0.4.5
=====
* Fixed a trailing slash bug for `RestController`s that have a `_lookup` method.
* Cleaned up the WSGI app reference from the threadlocal state on every request
  (to avoid potential memory leaks, especially when testing).
* Improved pecan documentation and correctd intersphinx references.
* pecan supports Python 3.4.

0.4.4
=====
* Removed memoization of certain controller attributes, which can lead to
  a memory leak in dynamic controller lookups.

0.4.3
=====
* Fixed several bugs for RestController.
* Fixed a bug in security handling for generic controllers.
* Resolved a bug in `_default` handlers used in `RestController`.
* Persist `pecan.request.context` across internal redirects.

0.4.2
=====
* Remove a routing optimization that breaks the WSME pecan plugin.

0.4.1
=====
* Moved the project to `StackForge infrastructure
  <http://ci.openstack.org/stackforge.html>`_, including Gerrit code review,
  Jenkins continuous integration, and GitHub mirroring.
* Added a pecan plugin for the popular `uwsgi server
  <http://uwsgi-docs.readthedocs.org>`_.
* Replaced the ``simplegeneric`` dependency with the new
  ``functools.singledispatch`` function in preparation for  Python 3.4 support.
* Optimized pecan's core dispatch routing for notably faster response times.

0.3.2
=====
* Made some changes to simplify how ``pecan.conf.app`` is passed to new apps.
* Fixed a routing bug for certain ``_lookup`` controller configurations.
* Improved documentation for handling file uploads.
* Deprecated the ``pecan.conf.requestviewer`` configuration option.

0.3.1
=====
* ``on_error`` hooks can now return a Pecan Response objects.
* Minor documentation and release tooling updates.

0.3.0
=====
* Pecan now supports Python 2.6, 2.7, 3.2, and 3.3.

0.2.4
=====
* Add support for ``_lookup`` methods as a fallback in RestController.
* A variety of improvements to project documentation.

0.2.3
=====
* Add a variety of optimizations to ``pecan.core`` that improve request
  handling time by approximately 30% for simple object dispatch routing.
* Store exceptions raised by ``abort`` in the WSGI environ so they can be
  accessed later in the request handling (e.g., by other middleware or pecan
  hooks).
* Make TransactionHook more robust so that it isn't as susceptible to failure
  when exceptions occur in *other* pecan hooks within a request.
* Rearrange quickstart verbiage so users don't miss a necessary step.

0.2.2
=====
* Unobfuscate syntax highlighting JavaScript for debian packaging.
* Extract the scaffold-building tests into tox.
* Add support for specifying a pecan configuration file via the
  ``PECAN_CONFIG``
  environment variable.
* Fix a bug in ``DELETE`` methods in two (or more) nested ``RestControllers``.
* Add documentation for returning specific HTTP status codes.

0.2.1
=====

* Include a license, readme, and ``requirements.txt`` in distributions.
* Improve inspection with ``dir()`` for ``pecan.request`` and ``pecan.response``
* Fix a bug which prevented pecan applications from being mounted at WSGI
  virtual paths.

0.2.0
=====

* Update base project scaffolding tests to be more repeatable.
* Add an application-level configuration option to disable content-type guessing by URL
* Fix the wrong test dependency on Jinja, it's Jinja2.
* Fix a routing-related bug in ``RestController``.  Fixes #156
* Add an explicit ``CONTRIBUTING.rst`` document.
* Improve visibility of deployment-related docs.
* Add support for a ``gunicorn_pecan`` console script.
* Remove and annotate a few unused (and py26 alternative) imports.
* Bug fix: don't strip a dotted extension from the path unless it has a matching mimetype.
* Add a test to the scaffold project buildout that ensures pep8 passes.
* Fix misleading output for ``$ pecan --version``.

0.2.0b
======

* Fix a bug in ``SecureController``.  Resolves #131.
* Extract debug middleware static file dependencies into physical files.
* Improve a test that can fail due to a race condition.
* Improve documentation about configation format and ``app.py``.
* Add support for content type detection via HTTP Accept headers.
* Correct source installation instructions in ``README``.
* Fix an incorrect code example in the Hooks documentation.
* docs: Fix minor typo in ``*args`` Routing example.
