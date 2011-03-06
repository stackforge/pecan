.. _installation:

Installation
============
We recommend installing Pecan with ``pip`` but you can also try with
``easy_install`` and ``virtualenv``. Creating a spot in your environment where
Pecan can be isolated from other packages is best practice.

To get started with an environment for Pecan, create a virtual environment for
it without any site-packages that might pollute::

    virtualenv --no-site-packages pecan-env
    cd pecan-env 
    source bin/activate

The above commands created a virtual environment and *activated* it. Those
actions will encapsulate anything that we do with the framework, making it
easier to debug problems if needed.

But we do not have Pecan yet, so let's grab it from PYPI::

    pip install pecan 

After a lot of output, you should have Pecan successfully installed and ready
to use.


Development (Unstable) Version
------------------------------
If you want to run the development version of Pecan you will
need GIT installed and clone the repo from github::

    git clone https://github.com/cleverdevil/pecan.git

If you are still in the *pecan-dev* virtual environment that we created before,
you should call ``setup.py`` to install::

    python setup.py develop