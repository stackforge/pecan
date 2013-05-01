"""
Shell command for Pecan.
"""
from pecan.commands import BaseCommand
from webtest import TestApp
from warnings import warn
import sys


class NativePythonShell(object):
    """
    Open an interactive python shell with the Pecan app loaded.
    """

    @classmethod
    def invoke(cls, ns, banner):  # pragma: nocover
        """
        :param ns: local namespace
        :param banner: interactive shell startup banner

        Embed an interactive native python shell.
        """
        import code
        py_prefix = sys.platform.startswith('java') and 'J' or 'P'
        shell_banner = 'Pecan Interactive Shell\n%sython %s\n\n' % \
            (py_prefix, sys.version)
        shell = code.InteractiveConsole(locals=ns)
        try:
            import readline  # noqa
        except ImportError:
            pass
        shell.interact(shell_banner + banner)


class IPythonShell(object):
    """
    Open an interactive ipython shell with the Pecan app loaded.
    """

    @classmethod
    def invoke(cls, ns, banner):  # pragma: nocover
        """
        :param ns: local namespace
        :param banner: interactive shell startup banner

        Embed an interactive ipython shell.
        Try the InteractiveShellEmbed API first, fall back on
        IPShellEmbed for older IPython versions.
        """
        try:
            from IPython.frontend.terminal.embed import (
                InteractiveShellEmbed
            )
            # try and load their default profile
            from IPython.frontend.terminal.ipapp import (
                load_default_config
            )
            config = load_default_config()
            shell = InteractiveShellEmbed(config=config, banner2=banner)
            shell(local_ns=ns)
        except ImportError:
            # Support for the IPython <= 0.10 shell API
            from IPython.Shell import IPShellEmbed
            shell = IPShellEmbed(argv=[])
            shell.set_banner(shell.IP.BANNER + '\n\n' + banner)
            shell(local_ns=ns, global_ns={})


class BPythonShell(object):
    """
    Open an interactive bpython shell with the Pecan app loaded.
    """

    @classmethod
    def invoke(cls, ns, banner):  # pragma: nocover
        """
        :param ns: local namespace
        :param banner: interactive shell startup banner

        Embed an interactive bpython shell.
        """
        from bpython import embed
        embed(ns, ['-i'], banner)


class ShellCommand(BaseCommand):
    """
    Open an interactive shell with the Pecan app loaded.
    Attempt to invoke the specified python shell flavor
    (ipython, bpython, etc.). Fall back on the native
    python shell if the requested flavor variance is not
    installed.
    """

    SHELLS = {
        'python': NativePythonShell,
        'ipython': IPythonShell,
        'bpython': BPythonShell,
    }

    arguments = BaseCommand.arguments + ({
        'name': ['--shell', '-s'],
        'help': 'which Python shell to use',
        'choices': SHELLS.keys(),
        'default': 'python'
    },)

    def run(self, args):
        """
        Load the pecan app, prepare the locals, sets the
        banner, and invokes the python shell.
        """
        super(ShellCommand, self).run(args)

        # load the application
        app = self.load_app()

        # prepare the locals
        locs = dict(__name__='pecan-admin')
        locs['wsgiapp'] = app
        locs['app'] = TestApp(app)

        model = self.load_model(app.config)
        if model:
            locs['model'] = model

        # insert the pecan locals
        from pecan import abort, conf, redirect, request, response
        locs['abort'] = abort
        locs['conf'] = conf
        locs['redirect'] = redirect
        locs['request'] = request
        locs['response'] = response

        # prepare the banner
        banner = '  The following objects are available:\n'
        banner += '  %-10s - This project\'s WSGI App instance\n' % 'wsgiapp'
        banner += '  %-10s - The current configuration\n' % 'conf'
        banner += '  %-10s - webtest.TestApp wrapped around wsgiapp\n' % 'app'
        if model:
            model_name = getattr(
                model,
                '__module__',
                getattr(model, '__name__', 'model')
            )
            banner += '  %-10s - Models from %s\n' % ('model', model_name)

        self.invoke_shell(locs, banner)

    def invoke_shell(self, locs, banner):
        """
        Invokes the appropriate flavor of the python shell.
        Falls back on the native python shell if the requested
        flavor (ipython, bpython,etc) is not installed.
        """
        shell = self.SHELLS[self.args.shell]
        try:
            shell().invoke(locs, banner)
        except ImportError as e:
            warn((
                "%s is not installed, `%s`, "
                "falling back to native shell") % (self.args.shell, e),
                RuntimeWarning
            )
            if shell == NativePythonShell:
                raise
            NativePythonShell().invoke(locs, banner)

    def load_model(self, config):
        """
        Load the model extension module
        """
        for package_name in getattr(config.app, 'modules', []):
            module = __import__(package_name, fromlist=['model'])
            if hasattr(module, 'model'):
                return module.model
        return None
