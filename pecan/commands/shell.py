"""
PasteScript shell command for Pecan.
"""
import sys

from webtest import TestApp

from base import Command


class ShellCommand(Command):
    """
    Open an interactive shell with the Pecan app loaded.
    """
    
    # command information
    usage = 'CONFIG_NAME'
    summary = __doc__.strip().splitlines()[0].rstrip('.')
    
    # command options/arguments
    min_args = 1
    max_args = 1
    
    def command(self):
        
        # load the application
        config = self.load_configuration(self.args[0])
        setattr(config.app, 'reload', False)
        app = self.load_app(config)
        
        # prepare the locals
        locs = dict(__name__='pecan-admin')
        locs['wsgiapp'] = app
        locs['app'] = TestApp(app)
        
        # find the model for the app
        model = self.load_model(config)
        if model:
            locs['model'] = model
        
        # insert the pecan locals
        exec('from pecan import abort, conf, redirect, request, response') in locs
        
        # prepare the banner
        banner = '  The following objects are available:\n'
        banner += '  %-10s - This project\'s WSGI App instance\n' % 'wsgiapp'
        banner += '  %-10s - The current configuration\n' % 'conf'
        banner += '  %-10s - webtest.TestApp wrapped around wsgiapp\n' % 'app'
        if model:
            model_name = getattr(model, '__module__', getattr(model, '__name__', 'model'))
            banner += '  %-10s - Models from %s\n' % ('model', model_name)
        
        # launch the shell, using IPython if available
        try:
            from IPython.Shell import IPShellEmbed
            shell = IPShellEmbed(argv=self.args)
            shell.set_banner(shell.IP.BANNER + '\n\n' + banner)
            shell(local_ns=locs, global_ns={})
        except ImportError:
            import code
            py_prefix = sys.platform.startswith('java') and 'J' or 'P'
            shell_banner = 'Pecan Interactive Shell\n%sython %s\n\n' % \
                (py_prefix, sys.version)
            shell = code.InteractiveConsole(locals=locs)
            try:
                import readline
            except ImportError:
                pass
            shell.interact(shell_banner + banner)
