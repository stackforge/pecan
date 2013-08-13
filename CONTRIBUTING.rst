Contributing to Pecan
---------------------
Pecan uses the Gerrit code review system for bug fixes and feature additions.

**Pull requests submitted through GitHub will be ignored.**

To contribute:

    * Visit `review.openstack.org <http://review.openstack.org>`_ and click the
      *Sign In* link at the top-right corner of the page.  Log in with your
      Launchpad ID (or register a new account).
    * ``$ git clone`` pecan locally and create a `topic branch
      <http://git-scm.com/book/ch3-4.html#Topic-Branches>`_ to hold your work.
      The general convention when working on bugs is to name the branch
      ``bug/BUG-NUMBER`` (e.g., ``bug/1234567``). Otherwise, give it
      a meaningful name because it will show up as the topic for your change in
      Gerrit.
    * Commit your work and submit a review (``$ git review``)

::

    $ git clone https://github.com/stackforge/pecan.git && cd pecan
    $ git checkout -b bug/1234
    $ pip install git-review && git review -s
    # Make changes
    $ pip install tox && tox
    $ git add .
    $ git commit -a
    $ git review

All contributions must:

    * Include accompanying tests.
    * Include narrative and API documentation if new features are added.
    * Be (generally) compliant with `PEP8
      <http://www.python.org/dev/peps/pep-0008/>`_.
    * Not break the test or build.  Before submitting a review, ``$ pip
      install tox && tox`` from your source to ensure that all tests still pass
      across multiple versions of Python.

Bugs should be filed on Launchpad, not GitHub:

https://bugs.launchpad.net/pecan
