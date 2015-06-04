__CONFIG_HELP__ = '''
<div class="traceback">
  <b>To disable this interface, set </b>
  <a target="window"
  href="https://pecan.readthedocs.org/en/latest/deployment.html#disabling-debug-mode">
    <pre>conf.app.debug = False</pre>
  </a>
</div>
'''  # noqa

try:
    import re
    from backlash.debug import DebuggedApplication

    class DebugMiddleware(DebuggedApplication):

        body_re = re.compile('(<body[^>]*>)', re.I)

        def debug_application(self, environ, start_response):
            for part in super(DebugMiddleware, self).debug_application(
                environ, start_response
            ):
                yield self.body_re.sub('\g<1>%s' % __CONFIG_HELP__, part)


except ImportError:
    from traceback import print_exc
    from pprint import pformat

    from mako.template import Template
    from six.moves import cStringIO as StringIO
    from webob import Response
    from webob.exc import HTTPException

    debug_template_raw = '''<html>
     <head>
      <title>Pecan - Application Error</title>
     <body>
      <header>
        <h1>
          An error occurred!
        </h1>
      </header>
      <div id="error-content">
        <p>
          %(config_help)s
          Pecan offers support for interactive debugging by installing the <a href="https://pypi.python.org/pypi/backlash" target="window">backlash</a> package:
          <br />
          <b><pre>pip install backlash</pre></b>
          ...and reloading this page.
        </p>
        <h2>Traceback</h2>
        <div id="traceback">
          <pre>${traceback}</pre>
        </div>
        <h2>WSGI Environment</h2>
        <div id="environ">
          <pre>${environment}</pre>
        </div>
      </div>
     </body>
    </html>
    ''' % {'config_help': __CONFIG_HELP__}  # noqa

    debug_template = Template(debug_template_raw)

    class DebugMiddleware(object):

        def __init__(self, app, *args, **kwargs):
            self.app = app

        def __call__(self, environ, start_response):
            try:
                return self.app(environ, start_response)
            except Exception as exc:
                # get a formatted exception
                out = StringIO()
                print_exc(file=out)

                # get formatted WSGI environment
                formatted_environ = pformat(environ)

                # render our template
                result = debug_template.render(
                    traceback=out.getvalue(),
                    environment=formatted_environ
                )

                # construct and return our response
                response = Response()
                if isinstance(exc, HTTPException):
                    response.status_int = exc.status
                else:
                    response.status_int = 500
                response.unicode_body = result
                return response(environ, start_response)
