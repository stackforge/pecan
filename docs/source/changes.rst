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
