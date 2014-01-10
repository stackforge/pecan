.. _installation:

Installation
============

Stable Version
--------------

We recommend installing Pecan with `pip
<http://www.pip-installer.org/>`_, but you
can also try with :command:`easy_install`. Creating a spot in your environment
where Pecan can be isolated from other packages is best practice.

To get started with an environment for Pecan, we recommend creating a new
`virtual environment <http://www.virtualenv.org>`_ using `virtualenv 
<http://www.virtualenv.org>`_::

    $ virtualenv pecan-env
    $ cd pecan-env 
    $ source bin/activate

The above commands create a virtual environment and *activate* it. This
will isolate Pecan's dependency installations from your system packages, making
it easier to debug problems if needed.

Next, let's install Pecan::

    $ pip install pecan 


Development (Unstable) Version
------------------------------
If you want to run the latest development version of Pecan you will
need to install git and clone the repo from GitHub::

    $ git clone https://github.com/stackforge/pecan.git

Assuming your virtual environment is still activated, call ``setup.py`` to
install the development version.::

    $ cd pecan
    $ python setup.py develop

.. note::
    The ``master`` development branch is volatile and is generally not
    recommended for production use.

Alternatively, you can also install from GitHub directly with ``pip``.::

    $ pip install -e git://github.com/stackforge/pecan.git#egg=pecan
