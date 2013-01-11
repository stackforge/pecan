Contributing to Pecan
---------------------
To fix bugs or add features to Pecan, a GitHub account is required.

The general practice for contributing is to `fork Pecan
<http://help.github.com/fork-a-repo/>`_ and make changes in the ``next``
branch.  When you're finished, `send a pull request
<http://help.github.com/send-pull-requests/>`_ and the developers will review
your patch.

All contributions must:

    * Include accompanying tests.
    * Include narrative and API documentation if new features are added.
    * Be (generally) compliant with `PEP8
      <http://www.python.org/dev/peps/pep-0008/>`_.
    * Not break the test or build.  Before issuing a pull request, ``$ pip
      install tox && tox`` from your source to ensure that all tests still pass
      across multiple versions of Python.
    * Add your name to the (bottom of the) AUTHORS file.
