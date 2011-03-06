.. _app_engine:

App Engine Support
===================

Pecan runs smoothly in Google's App Engine. There is **no** hacking/patching or weird 
changes that you need to make to work with Pecan. However, since App Engine has certain 
restrictions you may want to be aware on how to set it up correctly.

.. note::
    We do not discuss here how to get an App Engine environment here, nor App Engine 
    specifics that are not related to Pecan. For more info on App Engine go to 
    `their docs <http://code.google.com/appengine/docs/whatisgoogleappengine.html>`_


Dependencies
---------------
Pecan has a few dependencies and one of them is already supported by App Engine (WebOb)
so no need to grab that. Just so you are aware, this is the list of things that you absolutely need 
to grab:

 *  WebCore       >= 1.0.0
 *  simplegeneric >= 0.7
 *  Paste         >= 1.7.5.1
 *  PasteScript   >= 1.7.3
 *  formencode    >= 1.2.2
 *  WebTest       >= 1.2.2
 *  WebError      >= 0.10.3   

These are optional, depending on the templating engine you want to use. However, depending on your choice,
you might want to check that engine's dependencies as well. 

 *  Genshi >= 0.6
 *  Kajiki >= 0.3.1
 *  Mako >= 0.3
 
From this point forward, we will assume you are going to be using Mako (it is the recommended Pecan template
engine), to avoid describing third party dependencies.


Creating the project
---------------------
Create a directory called ``pecan_gae`` and ``cd`` into it so we can start adding files. We go step by 
step into what needs to go there to get everything running properly.

app.yaml
------------

To start off, you will need your ``app.yaml`` file set properly to map to Pecan. This is how that file should look
like::

    application: foo-bar
    version: 1
    runtime: python
    api_version: 1

    handlers:

    - url: /.*
      script: main.py

Remember the application name will have to match your registered app name in App Engine. The file above maps 
everything to a ``main.py`` file that we will create next.

This file will be the *root* of our project and will handle everything. 

main.py 
------------
You can name this anything you want, but for consistency we are going with `main.py`. This file will handle 
all the incoming requests including static files for our Pecan application. This is how it should look::

    from google.appengine.ext.webapp import util
    import sys
    if './lib' not in sys.path:
        sys.path.append('./lib')

    from pecan import Pecan, expose


    class RootController(object):

        @expose('kajiki:index.html')
        def index(self):
            return dict(name="Joe Wu Zap")


    def main():
        application = Pecan(RootController(), template_path='templates')
        util.run_wsgi_app(application)


    if __name__ == '__main__':
        main()

We are doing a few things here... first we are importing the ``util`` module from App Engine that will 
run our Pecan app, then we are importing ``sys`` because we need to add ``lib`` to our path.

The ``lib`` directory is where all our dependencies (including Pecan) will live, so we need to make sure
App Engine will see that as well as all our libraries within ``lib`` (it would not be enough to add a 
``__init__.py`` file there).


lib
-----
Go ahead and create a ``lib`` directory inside of your ``pecan_gae`` directory
application and add the requirements for Pecan there. Make sure you have
a ``__init__.py`` file too. 

The ``lib`` directory should contain the source for all the dependencies we need. For our example, it should
contain these libraries:

 * alacarte
 * formencode
 * mako
 * markupsafe
 * Paste 
 * pecan 
 * pygments
 * simplegeneric.py
 * simplejson
 * tempita
 * WebCore
 * WebTest
 * WebError

Unfortunately, `weberror` needs `pkg_resources` which it can't find. The easy
fix for this problem is to find `pkg_resources` in your own `site-packages`
directory and copy it inside `weberror`.

That is all you need to get this project started!

.. note::
    When grabing the source of the dependencies we mention, make sure you are actually grabing the module itself 
    and not adding the top directory source (where setup.py lives). Also make
    sure you are **not** using egg files (App Engine doesn't work with them).

templates
-----------
The `templates` directory is where we will have all of our html templates for Pecan. If you don't have it already, go ahead 
and create it and add this html file to it and name it index.html::

    <html>

    <head>
      <title>Hello, ${name}!</title>  
    </head>

    <body>
      <h1>Hello, ${name}!</h1>
    </body>

    </html>


Layout
---------
This is how your layout (only showing directories) should look like::

    pecan_gae
    ├── lib
    │   ├── alacarte
    │   │   ├── serialize
    │   │   └── template
    │   ├── formencode
    │   │   ├── javascript
    │   │   └── util
    │   ├── mako
    │   │   └── ext
    │   ├── markupSafe
    │   ├── paste
    │   │   ├── auth
    │   │   ├── cowbell
    │   │   ├── debug
    │   │   ├── evalexception
    │   │   │   └── media
    │   │   ├── exceptions
    │   │   └── util
    │   ├── pecan
    │   │   ├── commands
    │   │   └── templates
    │   │       └── project
    │   │           ├── +package+
    │   │           │   ├── controllers
    │   │           │   ├── model
    │   │           │   └── templates
    │   │           └── public
    │   │               ├── css
    │   │               └── javascript
    │   ├── pygments
    │   │   ├── filters
    │   │   ├── formatters
    │   │   ├── lexers
    │   │   └── styles
    │   ├── simplejson
    │   │   └── tests
    │   ├── tempita
    │   ├── web
    │   │   ├── app
    │   │   ├── auth
    │   │   ├── commands
    │   │   ├── core
    │   │   │   └── dialects
    │   │   ├── db
    │   │   ├── extras
    │   │   └── utils
    │   ├── webTest
    │   └── weberror
    │       ├── eval-media
    │       ├── exceptions
    │       └── util
    └── templates


Trying it out
-------------------------
Now everything should be ready to start serving, so go ahead and run the development server::

    $ ./dev_appserver.py pecan_gae 
    INFO     2010-10-10 12:44:29,476 dev_appserver_main.py:431] Running application pecan-gae on port 8080: http://localhost:8080
    

If you go to your browser and hit ``localhost:8080`` you should see something like this::

        Hello, Joe Wu Zap!

This is the most basic example for App Engine, you can start adding more controllers to handle a bigger 
application and connect everything together. 
