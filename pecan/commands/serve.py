"""
Serve command for Pecan.
"""
import os
import sys
import time
import subprocess

from pecan.commands import BaseCommand


class ServeCommand(BaseCommand):
    """
    Serves a Pecan web application.

    This command serves a Pecan web application using the provided
    configuration file for the server and application.
    """

    arguments = ({
        'command': 'config_file',
        'help': 'a Pecan configuration file'
    }, {
        'command': '--reload',
        'help': 'Watch for changes and automatically reload.',
        'default': False,
        'action': 'store_true'
    })

    def run(self, args):
        super(ServeCommand, self).run(args)
        app = self.load_app()
        self.serve(app, app.config)

    def create_subprocess(self):
        self.server_process = subprocess.Popen(
            [arg for arg in sys.argv if arg != '--reload'],
            stdout=sys.stdout, stderr=sys.stderr
        )

    def watch_and_spawn(self):
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        print 'Monitoring for changes...'
        self.create_subprocess()

        parent = self

        class AggressiveEventHandler(FileSystemEventHandler):
            def should_reload(self, path):
                extension = os.path.splitext(path)[1]
                if extension in (
                    '.py', '.pyc', '.html', '.mak',
                    '.mako', '.xml'
                ):
                    return True
                return False

            def on_modified(self, event):
                if self.should_reload(getattr(event, 'src_path', '')):
                    parent.server_process.kill()
                    parent.create_subprocess()

        event_handler = AggressiveEventHandler()
        observer = Observer()
        observer.schedule(event_handler, path=os.getcwd(), recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def _serve(self, app, conf):
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

    def serve(self, app, conf):
        """
        A very simple approach for a WSGI server.
        """

        if self.args.reload:
            try:
                self.watch_and_spawn()
            except ImportError:
                print('The `--reload` option requires `watchdog` to be '
                      'installed.')
                print('   $ pip install watchdog')
        else:
            self._serve(app, conf)
