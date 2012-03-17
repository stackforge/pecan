from cStringIO import StringIO
from traceback import print_exc
from pprint import pformat

from mako.template import Template

from webob import Response

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


debug_template_raw = '''<html>
 <head>
  <title>Pecan - Application Error</title>

  <style type="text/css">
    body {
      background: #311F00;
      color: white;
      font-family: 'Helvetica Neue', 'Helvetica', 'Verdana', sans-serif;
      padding: 2em;
    }

    a {
      color: #FAFF78;
      text-decoration: none;
    }

    a:hover {
      text-decoration: underline;
    }

    div#content  {
      width: 800px;
      margin: 0 auto;
    }

    form {
      margin: 0;
      padding: 0;
      border: 0;
    }

    fieldset {
      border: 0;
    }

    input.error {
      background: #FAFF78;
    }

    header {
      text-align: center;
    }

    h1, h2, h3, h4, h5, h6 {
      font-family: 'Futura', 'Helvetica', sans-serif;
    }

    h1 {
        font-size: 40px;
        color: #CD9A67;
    }

    pre {
        padding: 5px;
        font-size: 13px;
        font-family: Bitstream Vera Sans Mono,monospace;
    }

    div.highlight {
        background: #422f11;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    div.highlight pre {
        background-color: transparent;
        margin: 0;
        padding: 15px;
        border: none;
        overflow: auto;
    }

    ${styles}
  </style>
 </head>
 <body>


  <h1>
    <img style="padding-top: 10px"
         align="center" alt="pecan logo"
         width="120" height="38"
         src="${pecan_image}" />
    application error
  </h1>

  <div id="error-content">
    <h2>Traceback</h2>
    <div id="traceback">
      ${traceback}
    </div>

    <h2>WSGI Environment</h2>
    <div id="environ">
      ${environment}
    </div>
  </div>
 </body>
</html>
'''

debug_template = Template(debug_template_raw)


class DebugMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        assert not environ['wsgi.multiprocess'], (
            "The EvalException middleware is not usable in a "
            "multi-process environment")
        try:
            return self.app(environ, start_response)
        except:
            # get a formatted exception
            out = StringIO()
            print_exc(file=out)

            # get formatted WSGI environment
            formatted_environ = pformat(environ)

            formatter = HtmlFormatter(style='native')
            lexer = PythonLexer()
            styles = formatter.get_style_defs('.highlight')

            formatted_environ = highlight(
                formatted_environ, lexer, formatter
            )

            formatted_traceback = highlight(
                out.getvalue(), lexer, formatter
            )

            # render our template
            result = debug_template.render(
                traceback=formatted_traceback,
                environment=formatted_environ,
                styles=styles,
                pecan_image=pecan_image
            )

            # construct and return our response
            response = Response()
            response.status_int = 400
            response.unicode_body = result
            return response(environ, start_response)

pecan_image = "data:image/png;base64,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%3D"  # noqa
