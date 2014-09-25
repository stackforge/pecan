from traceback import print_exc
from pprint import pformat
import pdb

from six.moves import cStringIO as StringIO

from mako.template import Template
from webob import Response

from .resources import (pecan_image, xregexp_js, syntax_js, syntax_css, theme,
                        brush)


debug_template_raw = '''<html>
 <head>
  <title>Pecan - Application Error</title>

  <link rel="stylesheet" type="text/css" href="${syntax_css}" />
  <link rel="stylesheet" type="text/css" href="${theme}" />

  <script type="text/javascript" src="${xregexp_js}"></script>
  <script type="text/javascript" src="${syntax_js}">
    /**
     * SyntaxHighlighter
     * http://alexgorbatchev.com/SyntaxHighlighter
     *
     * SyntaxHighlighter is donationware. If you are using it, please donate.
     * http://alexgorbatchev.com/SyntaxHighlighter/donate.html
     *
     * @version
     * 3.0.83 (July 02 2010)
     *
     * @copyright
     * Copyright (C) 2004-2010 Alex Gorbatchev.
     *
     * @license
     * Dual licensed under the MIT and GPL licenses.
     */
  </script>
  <script type="text/javascript" src="${brush}">
    /**
     * SyntaxHighlighter
     * http://alexgorbatchev.com/SyntaxHighlighter
     *
     * SyntaxHighlighter is donationware. If you are using it, please donate.
     * http://alexgorbatchev.com/SyntaxHighlighter/donate.html
     *
     * @version
     * 3.0.83 (July 02 2010)
     *
     * @copyright
     * Copyright (C) 2004-2010 Alex Gorbatchev.
     *
     * @license
     * Dual licensed under the MIT and GPL licenses.
     */
  </script>

  <style type="text/css">
    body {
      color: #000;
      background: #FFF;
      font-family: 'Helvetica Neue', 'Helvetica', 'Verdana', sans-serif;
      font-size: 12px;
      padding: 0;
      margin: 0;
    }

    a {
      color: #FAFF78;
    }

    h1, h2, h3, h4, h5, h6 {
      font-family: 'Helvetica', sans-serif;
    }

    h1 {
      margin: 0;
      padding: .75em 1.5em 1em 1.5em;
      color: #F90;
      font-size: 14px;
      font-weight: bold;
    }

    h1 img  {
      padding-right: 5px;
    }

    h2 {
      color: #311F00;
    }

    header  {
      width: 100%;
      background: #311F00;
    }

    div#error-content  {
      padding: 0 2em;
    }

    .syntaxhighlighter a,
    .syntaxhighlighter div,
    .syntaxhighlighter code,
    .syntaxhighlighter table,
    .syntaxhighlighter table td,
    .syntaxhighlighter table tr,
    .syntaxhighlighter table tbody,
    .syntaxhighlighter table thead,
    .syntaxhighlighter table caption,
    .syntaxhighlighter textarea {
      font-family: monospace !important;
    }

    .syntaxhighlighter .container {
       background: #FDF6E3 !important;
       padding: 1em !important;
    }

    .syntaxhighlighter .container .line {
       background: #FDF6E3 !important;
    }

    .syntaxhighlighter .container .line .python.string {
       color: #C70 !important;
    }

    #debug {
        background: #FDF6E3;
        padding: 10px !important;
        margin-top: 10px;
        font-family: monospace;
    }

  </style>
  <script type="text/javascript">
      SyntaxHighlighter.defaults['gutter'] = false;
      SyntaxHighlighter.defaults['toolbar'] = false;
      SyntaxHighlighter.all()
  </script>

  <script type="text/javascript">
    function get_request() {
        /* ajax sans jquery makes me sad */
        var request = false;

        // Mozilla/Safari
        if (window.XMLHttpRequest) {
            request = new XMLHttpRequest();
        }

        // IE
        else if (window.ActiveXObject) {
            request = new ActiveXObject("Microsoft.XMLHTTP");
        }

        return request;
    }

    function debug_request(btn) {
        btn.disabled = true;

        request = get_request();
        request.open('GET', '/__pecan_initiate_pdb__', true);
        request.onreadystatechange = function() {
            if (request.readyState == 4) {
                btn.disabled = false;
            }
        }
        request.send('');

        /* automatically timeout after 5 minutes, re-enabling the button */
        setTimeout(function() {
           request.abort();
        }, 5 * 60 * 1000);
    }
  </script>
 </head>
 <body>

  <header>
    <h1>
      <img style="padding-top: 7px"
           align="center" alt="pecan logo"
           height="25"
           src="${pecan_image}" />
      application error
    </h1>
  </header>

  <div id="error-content">

    <p>
      <b>To disable this interface, set </b>
      <pre class="brush: python">conf.app.debug = False</pre>
    </p>

    <h2>Traceback</h2>
    <div id="traceback">
      <pre class="brush: python">${traceback}</pre>
    </div>

    % if not debugging:
    <b>Want to debug this request?</b>
    <div id="debug">
      You can <button onclick="debug_request(this)">
        repeat this request
      </button> with a Python debugger breakpoint.
    </div>
    % endif

    <h2>WSGI Environment</h2>
    <div id="environ">
      <pre class="brush: python">${environment}</pre>
    </div>
  </div>
 </body>
</html>
'''

debug_template = Template(debug_template_raw)
__debug_environ__ = None


class PdbMiddleware(object):
    def __init__(self, app, debugger):
        self.app = app
        self.debugger = debugger

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except:
            self.debugger()


class DebugMiddleware(object):
    """A WSGI middleware that provides debugging assistance for development
    environments.

    To enable the debugging middleware, simply set the ``debug`` flag to
    ``True`` in your configuration file::

        app = {
            ...
            'debug': True,
            ...
        }

    Once enabled, the middleware will automatically catch exceptions raised by
    your application, and display the Python stack trace and WSGI environment
    in your browser for easy debugging.

    To further aid in debugging, the middleware includes the ability to repeat
    the offending request, automatically inserting a breakpoint, and dropping
    your console into the Python debugger, ``pdb``.

    For more information, refer to the  `documentation for pdb
    <http://docs.python.org/library/pdb.html>`_ available on the Python
    website.

    :param app: the application to wrap.
    :param debugger: a callable to start debugging, defaulting to the Python
                     debugger, ``pdb``.
    """

    def __init__(self, app, debugger=pdb.post_mortem):
        self.app = app
        self.debugger = debugger

    def __call__(self, environ, start_response):
        if environ['wsgi.multiprocess']:
            raise RuntimeError(
                "The DebugMiddleware middleware is not usable in a "
                "multi-process environment"
            )

        if environ.get('paste.testing'):
            return self.app(environ, start_response)

        # initiate a PDB session if requested
        global __debug_environ__
        debugging = environ['PATH_INFO'] == '/__pecan_initiate_pdb__'
        if debugging:
            PdbMiddleware(self.app, self.debugger)(
                __debug_environ__, start_response
            )
            environ = __debug_environ__

        try:
            return self.app(environ, start_response)
        except:
            # save the environ for debugging
            if not debugging:
                __debug_environ__ = environ

            # get a formatted exception
            out = StringIO()
            print_exc(file=out)

            # get formatted WSGI environment
            formatted_environ = pformat(environ)

            # render our template
            result = debug_template.render(
                traceback=out.getvalue(),
                environment=formatted_environ,
                pecan_image=pecan_image,
                xregexp_js=xregexp_js,
                syntax_js=syntax_js,
                brush=brush,
                syntax_css=syntax_css,
                theme=theme,
                debugging=debugging
            )

            # construct and return our response
            response = Response()
            response.status_int = 400
            response.unicode_body = result
            return response(environ, start_response)
