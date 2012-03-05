.. _installation:

Installation
============

Stable Version
------------------------------

We recommend installing Pecan with ``pip`` but you can also try with
``easy_install`` and ``virtualenv``. Creating a spot in your environment where
Pecan can be isolated from other packages is best practice.

To get started with an environment for Pecan, create a new
`virtual environment <http://www.virtualenv.org>`_::

    virtualenv pecan-env
    cd pecan-env 
    source bin/activate

The above commands create a virtual environment and *activate* it. Those
actions will encapsulate any dependency installations for the framework,
making it easier to debug problems if needed.

Next, let's install Pecan::

    pip install pecan 

After a lot of output, you should have Pecan successfully installed.


Development (Unstable) Version
------------------------------
If you want to run the development version of Pecan you will
need to install git and clone the repo from GitHub::

    git clone https://github.com/dreamhost/pecan.git

If your virtual environment is still activated, call ``setup.py`` to install
the development version::

    cd pecan
    python setup.py develop

...alternatively, you can also install from GitHub directly with ``pip``::

    pip install -e git://github.com/dreamhost/pecan.git#egg=pecan
