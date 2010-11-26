.. _installation:

Installation
============
We recommend installing Pecan with ``pip`` but you can also try with
``easy_install`` and ``virtualenv``. Creating a spot in your environment where
Pecan can be isolated from other packages is best practice.

To get started with an environment for Pecan, create a virtual environment for
it without any site-packages that might pollute::

    virtualenv --no-sitpackages pecan-env
    cd pecan-env 
    source bin/activate

The above commands created a virtual environment and *activated* it. Those
actions will encapsulate anything that we do with the framework, making it
easier to debug problems if needed.

But we do not have Pecan yet, so let's grab it from PYPI::

    pip install pecan 

After a lot of output, you should have Pecan successfully installed and ready
to use.

.. note::
    If you want to run the development (unstable) version of Pecan you will
    need GIT and clone the repo from: https://github.com/cleverdevil/pecan.git 

    
