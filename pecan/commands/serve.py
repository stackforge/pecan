"""
PasteScript serve command for Pecan
"""
from paste.script.serve import ServeCommand as PasteServeCommand
from base import Command

class ServeCommand(PasteServeCommand, Command):
    min_args = 0
    usage = 'CONFIG_FILE [start|stop|restart|status]'
    summary = "Serve the pecan web application"
    description = """\
    This command serves a pecan web application using the provided
    configuration file for the server and application.  
       
    If start/stop/restart is given, then --daemon is implied, and it will
    start (normal operation), stop (--stop-daemon), or do both.
    """
        
    def __init__(self, *args, **kwargs):
        super(ServeCommand, self).__init__(*args, **kwargs)

        # remove the commands we don't support
        self.parser.remove_option('-n')
        self.parser.remove_option('-s')
        self.parser.remove_option('--server-name')

    # Since we're trying to fit into Paste Scripts Serve command
    # we're accepting all args because we're ignoring them
    def loadapp(self, *args, **kwargs):
        config = self.load_configuration(self.args[0])
        # note: self.load_app from the Pecan command base 
        return (self.load_app(config), config)

    # return a serve function that uses our result of loadapp
    def loadserver(self, *args, **kwargs):
        from paste import httpserver

        def server(app_tuple):
            app, config = app_tuple
            httpserver.serve(app, config.server.host, config.server.port)

        return server

    def logging_file_config(self, config_file):
        # XXX log file options are not currently supported
        pass

