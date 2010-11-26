.. Pecan documentation master file, created by
   sphinx-quickstart on Sat Oct  9 14:41:27 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pecan's documentation
=========================

A WSGI object-dispatching web framework, in the spirit of TurboGears, only 
much much smaller, with many fewer dependencies.


Contents:

.. toctree::
   :maxdepth: 2

   installation.rst
   routing.rst 
   configuration.rst 
   templates.rst 
   hooks.rst 
   jsonify.rst 
   secure_controller.rst 
   validation_n_errors.rst


Introduction
============
Pecan packs a few good features but it is also extremely lean, it requires just
a few dependencies but for the most part it feels like a full fledged web
framework!

 * Object-Dispatch for easy routing
 * Pre and Post Hooks 
 * REST controllers 
 * Validation and Error handling
 * Secure controllers
 * Template language support
 * AppEngine out of the box (no patching!)



Pecan Hello World
------------------
In this example we use ``httpserver`` from ``paste`` but feel free to use any 
WSGI server you want::

    from paste import httpserver
    from pecan import make_app, expose


    class RootController(object):

        @expose()
        def index(self):
            return 'Hello, World!'

    app = make_app(RootController(), debug=True)
    httpserver.serve(app, host='0.0.0.0', port=8080)


Tutorials
=========
We provide a couple of easy ways to get started including a short tutorial on
App Engine.

.. toctree::
   :maxdepth: 2

   quick_start.rst 
   app_engine.rst


API
===
The following section lists the main sections of Pecan, where you can find more
specific details about methods and modules available.

.. toctree::
   :maxdepth: 2

   decorators.rst 
   hooks.rst 
   jsonify.rst 
   pecan.rst 
   rest.rst 
   routing.rst 
   secure.rst
   templating.rst

License
-------
The Pecan framework and the documentation is BSD Licensed::

    Copyright (c) <2010>, <Pecan Framework>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:
        * Redistributions of source code must retain the above copyright
          notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above copyright
          notice, this list of conditions and the following disclaimer in the
          documentation and/or other materials provided with the distribution.
        * Neither the name of the <organization> nor the
          names of its contributors may be used to endorse or promote products
          derived from this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
    DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



