Introduction and History
========================
Welcome to Pecan, a lean Python web framework inspired by CherryPy,
TurboGears, and Pylons. Pecan was originally created by the developers
of `ShootQ <http://shootq.com>`_ while working at `Pictage
<http://pictage.com>`_.

Pecan was created to fill a void in the Python web-framework world – a
very lightweight framework that provides object-dispatch style
routing.  Pecan does not aim to be a "full stack" framework, and
therefore includes no out of the box support for things like sessions
or databases (although tutorials are included for integrating these
yourself in just a few lines of code). Pecan instead focuses on HTTP
itself.

Although it is lightweight, Pecan does offer an extensive feature set
for building HTTP-based applications, including:

 * Object-dispatch for easy routing
 * Full support for REST-style controllers
 * Extensible security framework
 * Extensible template language support
 * Extensible JSON support
 * Easy Python-based configuration

Narrative Documentation
=======================

.. toctree::
   :maxdepth: 2
   
   installation.rst
   quick_start.rst   
   routing.rst
   templates.rst
   rest.rst
   configuration.rst
   secure_controller.rst
   hooks.rst
   jsonify.rst
   commands.rst
   development.rst
   deployment.rst
   logging.rst
   testing.rst


Cookbook and Common Patterns
============================
.. toctree::
   :maxdepth: 2

   forms.rst
   sessions.rst
   databases.rst
   errors.rst
   simple_forms_processing.rst
   simple_ajax.rst


API Documentation
=================
Pecan's source code is well documented using Python docstrings and 
comments. In addition, we have generated API documentation from the
docstrings here:


.. toctree::
   :maxdepth: 2
   
   pecan_core.rst
   pecan_commands.rst
   pecan_configuration.rst
   pecan_decorators.rst
   pecan_deploy.rst
   pecan_hooks.rst
   pecan_middleware_debug.rst
   pecan_jsonify.rst
   pecan_rest.rst
   pecan_routing.rst
   pecan_secure.rst
   pecan_templating.rst
   pecan_testing.rst
   pecan_util.rst


Change History
=================

.. toctree::
   :maxdepth: 1

   changes.rst


License
-------
The Pecan framework and the documentation is BSD Licensed::

    Copyright (c) <2010>, Pecan Framework
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



