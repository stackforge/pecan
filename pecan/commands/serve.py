"""
Serve command for Pecan.
"""
import os
from pecan.commands import BaseCommand


class ServeCommand(BaseCommand):
    """
    Serves a Pecan web application.

    This command serves a Pecan web application using the provided
    configuration file for the server and application.
    """

    def run(self, args):
        super(ServeCommand, self).run(args)
        app = self.load_app()
        self.serve(app, app.config)

    def serve(self, app, conf):
        """
        A very simple approach for a WSGI server.
        """
        from wsgiref.simple_server import make_server
        host, port = conf.server.host, int(conf.server.port)
        srv = make_server(host, port, app)
        print 'Starting server in PID %s' % os.getpid()
        if host == '0.0.0.0':
            print 'serving on 0.0.0.0:%s, view at http://127.0.0.1:%s' % \
                (port, port)
        else:
            print "serving on http://%s:%s" % (host, port)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            # allow CTRL+C to shutdown
            pass
