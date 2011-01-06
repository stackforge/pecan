"""
PasteScript commands for Pecan.
"""
from configuration import _runtime_conf, set_config
from paste.script import command as paste_command
from paste.script.create_distro import CreateDistroCommand
from webtest import TestApp

from templates import DEFAULT_TEMPLATE

import copy
import optparse
import os
import pkg_resources
import sys
import warnings


class CommandRunner(object):
    """
    Dispatches command execution requests.
    
    This is a custom PasteScript command runner that is specific to Pecan 
    commands. For a command to show up, its name must begin with "pecan-". 
    It is also recommended that its group name be set to "Pecan" so that it 
    shows up under that group when using ``paster`` directly.
    """
    
    def __init__(self):
        
        # set up the parser
        self.parser = optparse.OptionParser(add_help_option=False,
                                            version='Pecan %s' % self.get_version(),
                                            usage='%prog [options] COMMAND [command_options]')
        self.parser.disable_interspersed_args()
        self.parser.add_option('-h', '--help',
                               action='store_true',
                               dest='show_help',
                               help='show detailed help message')
        
        # suppress BaseException.message warnings for BadCommand
        if sys.version_info < (2, 7):
            warnings.filterwarnings(
                'ignore', 
                'BaseException\.message has been deprecated as of Python 2\.6', 
                DeprecationWarning, 
                paste_command.__name__.replace('.', '\\.'))
        
        # register Pecan as a system plugin when using the custom runner
        paste_command.system_plugins.append('Pecan')
    
    def get_command_template(self, command_names):
        if not command_names:
            max_length = 10
        else:
            max_length = max([len(name) for name in command_names])
        return '  %%-%ds  %%s\n' % max_length
    
    def get_commands(self):
        commands = {}
        for name, command in paste_command.get_commands().iteritems():
            if name.startswith('pecan-'):
                commands[name[6:]] = command.load()
        return commands
    
    def get_version(self):
        try:
            dist = pkg_resources.get_distribution('Pecan')
            if os.path.dirname(os.path.dirname(__file__)) == dist.location:
                return dist.version
            else:
                return '(development)'
        except:
            return '(development)'
    
    def print_usage(self, file=sys.stdout):
        self.parser.print_help(file=file)
        file.write('\n')
        command_groups = {}
        commands = self.get_commands()
        if not commands:
            file.write('No commands registered.\n')
            return
        command_template = self.get_command_template(commands.keys())
        for name, command in commands.iteritems():
            group_name = command.group_name
            if group_name.lower() == 'pecan':
                group_name = ''
            command_groups.setdefault(group_name, {})[name] = command
        command_groups = sorted(command_groups.items())
        for i, (group, commands) in enumerate(command_groups):
            file.write('%s:\n' % (group or 'Commands'))
            for name, command in sorted(commands.items()):
                file.write(command_template % (name, command.summary))
            if i + 1 < len(command_groups):
                file.write('\n')
    
    def print_known_commands(self, file=sys.stderr):
        commands = self.get_commands()
        command_names = sorted(commands.keys())
        if not command_names:
            file.write('No commands registered.\n')
            return
        file.write('Known commands:\n')
        command_template = self.get_command_template(command_names)
        for name in command_names:
            file.write(command_template % (name, commands[name].summary))
    
    def run(self, args):
        options, args = self.parser.parse_args(args)
        if not args:
            self.print_usage()
            return 0
        command_name = args.pop(0)
        commands = self.get_commands()
        if command_name not in commands:
            sys.stderr.write('Command %s not known\n\n' % command_name)
            self.print_known_commands()
            return 1
        else:
            command = commands[command_name](command_name)
            if options.show_help:
                return command.run(['-h'])
            else:
                return command.run(args)
    
    @classmethod
    def handle_command_line(cls):
        try:
            runner = CommandRunner()
            exit_code = runner.run(sys.argv[1:])
        except paste_command.BadCommand, ex:
            sys.stderr.write('%s\n' % ex)
            exit_code = ex.exit_code
        sys.exit(exit_code)


class Command(paste_command.Command):
    """
    Base class for Pecan commands.
    
    This provides some standard functionality for interacting with Pecan 
    applications and handles some of the basic PasteScript command cruft.
    
    See ``paste.script.command.Command`` for more information.
    """
    
    # command information
    group_name = 'Pecan'
    summary = ''
    
    # command parser
    parser = paste_command.Command.standard_parser()
    
    def run(self, args):
        try:
            return paste_command.Command.run(self, args)
        except paste_command.BadCommand, ex:
            ex.args[0] = self.parser.error(ex.args[0])
            raise
    
    def can_import(self, name):
        try:
            __import__(name)
            return True
        except ImportError:
            return False
    
    def get_package_names(self, config):
        if not hasattr(config.app, 'modules'):
            return []
        return [module.__name__ for module in config.app.modules if hasattr(module, '__name__')]
    
    def load_configuration(self, name):
        set_config(name)
        return _runtime_conf
    
    def load_app(self, config):
        for package_name in self.get_package_names(config):
            module_name = '%s.app' % package_name
            if self.can_import(module_name):
                module = sys.modules[module_name]
                if hasattr(module, 'setup_app'):
                    return module.setup_app(config)
        raise paste_command.BadCommand('No app.setup_app found in any of the configured app.modules')
    
    def load_model(self, config):
        for package_name in self.get_package_names(config):
            module_name = '%s.model' % package_name
            if self.can_import(module_name):
                return sys.modules[module_name]
        return None
    
    def command(self):
        pass


class ServeCommand(Command):
    """
    Serve the described application.
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
        app = self.load_app(config)
        
        from paste import httpserver
        try:
            httpserver.serve(app, config.server.host, config.server.port)
        except KeyboardInterrupt:
            print '^C'


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


class CreateCommand(CreateDistroCommand, Command):
    """
    Creates the file layout for a new Pecan distribution.
    
    For a template to show up when using this command, its name must begin 
    with "pecan-". Although not required, it should also include the "Pecan" 
    egg plugin for user convenience.
    """
    
    # command information
    summary = __doc__.strip().splitlines()[0].rstrip('.')
    description = None
    
    def command(self):
        if not self.options.list_templates:
            if not self.options.templates:
                self.options.templates = [DEFAULT_TEMPLATE]
        try:
            return CreateDistroCommand.command(self)
        except LookupError, ex:
            sys.stderr.write('%s\n\n' % ex)
            CreateDistroCommand.list_templates(self)
            return 2
    
    def all_entry_points(self):
        entry_points = []
        for entry in CreateDistroCommand.all_entry_points(self):
            if entry.name.startswith('pecan-'):
                entry = copy.copy(entry)
                entry_points.append(entry)
                entry.name = entry.name[6:]
        return entry_points
