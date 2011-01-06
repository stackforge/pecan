"""
Commands for Pecan, heavily inspired by Paste Script commands.
"""
from configuration import _runtime_conf, set_config
from webtest import TestApp

from templates import Template

import imp
import optparse
import os
import pkg_resources
import re
import sys
import textwrap


class CommandRunner(object):
    """
    Dispatches command execution requests.
    """
    
    def __init__(self):
        self.parser = optparse.OptionParser(add_help_option=False,
                                            version='Pecan %s' % self.get_version(),
                                            usage='%prog [options] COMMAND [command_options]')
        self.parser.disable_interspersed_args()
        self.parser.add_option('-h', '--help',
                               action='store_true',
                               dest='show_help',
                               help='show detailed help message')
    
    def get_command_template(self, command_names):
        if not command_names:
            max_length = 10
        else:
            max_length = max([len(name) for name in command_names])
        return '  %%-%ds  %%s\n' % max_length
    
    def get_commands(self, cls=None):
        commands = {}
        if not cls:
            cls = Command
        for command in cls.__subclasses__():
            if hasattr(command, 'name'):
                commands[command.name] = command
            commands.update(self.get_commands(command))
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
            command_groups.setdefault(command.group_name, {})[name] = command
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
            command = commands[command_name]()
            if options.show_help:
                return command('-h')
            else:
                return command(*args)
    
    @classmethod
    def handle_command_line(cls):
        try:
            runner = CommandRunner()
            exit_code = runner.run(sys.argv[1:])
        except CommandException, ex:
            sys.stderr.write('%s\n' % ex)
            exit_code = ex.exit_code
        sys.exit(exit_code)


class Command(object):
    """
    Base class for Pecan commands.
    
    All commands should inherit from this class or one of its subclasses. To 
    be exposed, subclasses must at least define a `name` class attribute.
    
    In addition, subclasses can define the following class attributes:
    
    - `group_name`: Group the command under this category in help messages.
    
    - `usage`: Usage information for the command. This is particularly useful 
      if your command accepts positional arguments in addition to standard 
      options.
    
    - `summary`: Short description for the command that appears in help 
      messages.
    
    - `description`: Longer description for the command that appears in its 
      help message only.
    
    - `required_options`: Tuple of 2-element tuples with the destination 
      variable name and option name for required options. If any of these are 
      not found after parsing the options, the command will abort.
    
    - `required_options_error`: The error message to display when a required 
      option is missing. This gets the variable name as `name` and the option 
      name as `option`.
    
    - `required_args`: Tuple of required argument names. If the provided list 
      of positional arguments is shorter than this, the command will abort.
    
    - `required_args_error`: The error message to display when a required 
      positional argument is missing. This gets the number of actual arguments 
      as `actual`, the number of missing arguments as `missing`, and the names 
      of missing arguments, comma separated, as `missing_names`.
    
    - `maximum_args`: The maximum number of arguments this command accepts. 
      If not `None` and the number of arguments exceeds this number, the 
      command will abort.
    
    - `maximum_args_error`: The error message to display when the number of 
      positional arguments exceeds the maximum number for the command. This 
      gets the number of actual arguments as `actual` and the maximum number 
      of arguments as `max`.
    
    - `default_verbosity`: The default verbosity for the command. This gets 
      increased by 1 for every `-v` option and decreased by 1 for every `-q` 
      option using the default option parser and stored as the `verbosity` 
      instance attribute. If you override how `-v` and `-q` work, the default 
      remains unchanged.
    
    - `return_code`: The default return for the command. If a subclass's 
      implementation of `run` doesn't return a value, this gets returned.
    
    Subclasses should override `run` to provide a command's specific 
    implementation. `run` should return a valid exit code (i.e., usually 0 
    for successful). See also `return_code` above.
    
    If a command has custom options, its subclass should override `get_parser` 
    to provide a custom `OptionParser`. It is recommended to call the parent 
    `get_parser` to get the default verbosity options, but this is not 
    required for a command to work.
    
    No other methods should be overriden by subclasses.
    """
    
    # command information
    group_name = ''
    usage = ''
    summary = ''
    description = ''
    
    # command options/arguments
    required_options = ()
    required_options_error = 'You must provide the option %(option)s'
    required_args = ()
    required_args_error = 'You must provide the following arguments: %(missing_names)s'
    maximum_args = None
    maximum_args_error = 'You must provide no more than %(max)s arguments'
    
    # command execution
    default_verbosity = 0
    return_code = 0
    
    def __call__(self, *args):
        
        # parse the arguments
        self.parser = self.get_parser()
        options, args = self.parse_args(list(args))
        
        # determine the verbosity
        for name, value in [('quiet', 0), ('verbose', 0)]:
            if not hasattr(options, name):
                setattr(options, name, value)
        self.verbosity = self.default_verbosity
        if isinstance(options.verbose, int):
            self.verbosity += options.verbose
        if isinstance(options.quiet, int):
            self.verbosity -= options.quiet
        
        # make sure all required options were provided
        for name, option in self.required_options:
            if not hasattr(options, name):
                message = self.required_options_error % {'name': name, 'option': option}
                raise CommandException(self.parser.error(message))
        
        # make sure all required arguments were provided
        if len(args) < len(self.required_args):
            missing = self.required_args[len(args):]
            message = self.required_args_error % {'actual': len(args), 
                                                  'missing': len(missing), 
                                                  'missing_names': ', '.join(missing)}
            raise CommandException(self.parser.error(message))
        
        # make sure not too many arguments were provided if there's a limit
        if self.maximum_args and len(args) > self.maximum_args:
            message = self.maximum_args_error % {'actual': len(args), 
                                                 'max': self.maximum_args}
            raise CommandException(self.parser.error(message))
        
        # execute the command
        result = self.run(options, args)
        if result is None:
            result = self.return_code
        return result
    
    def can_import(self, name):
        """
        Attempt to __import__ the specified package/module, returning
        True when succeeding, otherwise False.
        """
        try:
            __import__(name)
            return True
        except ImportError:
            return False
    
    def get_package_names(self, config):
        if not hasattr(config.app, 'modules'):
            return []
        return [module.__name__ for module in config.app.modules if hasattr(module, '__name__')]
    
    def get_parser(self):
        parser = optparse.OptionParser()
        parser.add_option('-v', '--verbose',
                          action='count',
                          dest='verbose',
                          help='increase verbosity')
        parser.add_option('-q', '--quiet',
                          action='count',
                          dest='quiet',
                          help='decrease verbosity')
        return parser
    
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
        raise CommandException('No app.setup_app found in any of the configured app.modules')
    
    def load_model(self, config):
        for package_name in self.get_package_names(config):
            module_name = '%s.model' % package_name
            if self.can_import(module_name):
                return sys.modules[module_name]
        return None
    
    def parse_args(self, args):
        if self.usage:
            usage = ' ' + self.usage
        else:
            usage = ''
        self.parser.usage = "%%prog %s [options]%s\n%s" % (self.name, usage, self.summary)
        if self.description:
            self.parser.description = textwrap.dedent(self.description)
        return self.parser.parse_args(args)
    
    def run(self, options, args):
        pass


class CommandException(Exception):
    """
    Raised when a command fails. Use CommandException in commands instead of 
    Exception so that these are correctly reported when running from the 
    command line. The optional `exit_code`, which defaults to 1, will be used 
    as the system exit code when running from the command line.
    """
    
    def __init__(self, message, exit_code=1):
        Exception.__init__(self, message)
        self.exit_code = exit_code


class ServeCommand(Command):
    """
    Serve the described application.
    """
    
    # command information
    name = 'serve'
    usage = 'CONFIG_NAME'
    summary = __doc__.strip().splitlines()[0].rstrip('.')
    
    # command options/arguments
    required_args = ('CONFIG_NAME', )
    maximum_args = 1
    
    def run(self, options, args):
        
        # load the application
        config = self.load_configuration(args[0])
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
    name = 'shell'
    usage = 'CONFIG_NAME'
    summary = __doc__.strip().splitlines()[0].rstrip('.')
    
    # command options/arguments
    required_args = ('CONFIG_NAME', )
    maximum_args = 1
    
    def run(self, options, args):
        
        # load the application
        config = self.load_configuration(args[0])
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


class CreateCommand(Command):
    """
    Creates a new Pecan package using a template.
    """
    
    # command information
    name = 'create'
    usage = 'PACKAGE_NAME'
    summary = __doc__.strip().splitlines()[0].rstrip('.')
    
    # command options/arguments
    maximum_args = 1
    
    # regex for package names
    BAD_CHARS_RE = re.compile(r'[^a-zA-Z0-9_]')
    
    def run(self, options, args):
        
        # if listing templates, list and return
        if options.list_templates:
            self.list_templates()
            return
        
        # check the specified template
        template_name = options.template or 'default'
        template = Template.get_templates().get(template_name)
        if not template:
            message = 'Template "%s" could not be found' % template_name
            raise CommandException(self.parser.error(message))
        
        # make sure a package name was specified
        if not args:
            message = 'You must provide a package name'
            raise CommandException(self.parser.error(message))
        
        # prepare the variables
        template = template()
        dist_name = args[0].lstrip(os.path.sep)
        output_dir = os.path.join(options.output_dir, dist_name)
        pkg_name = self.BAD_CHARS_RE.sub('', dist_name.lower())
        egg_name = pkg_resources.to_filename(pkg_resources.safe_name(dist_name))
        vars = {
            'project':  dist_name,
            'package':  pkg_name,
            'egg':      egg_name
        }
        
        # display the vars if verbose
        if self.verbosity:
            self.display_vars(vars)
        
        # create the template
        self.create_template(template, output_dir, vars, overwrite=options.overwrite)
    
    def get_parser(self):
        parser = Command.get_parser(self)
        parser.add_option('-t', '--template',
                          dest='template',
                          metavar='TEMPLATE',
                          help='template to use (uses default if not specified)')
        parser.add_option('-o', '--output-dir',
                          dest='output_dir',
                          metavar='DIR',
                          default='.',
                          help='output to DIR (defaults to current directory)')
        parser.add_option('--list-templates',
                          dest='list_templates',
                          action='store_true',
                          help='show all available templates')
        parser.add_option('-f', '--overwrite',
                          dest='overwrite',
                          action='store_true',
                          help='Overwrite files',
                          default=False)
        return parser
    
    def create_template(self, template, output_dir, vars, overwrite=False):
        if self.verbosity:
            print 'Creating template %s' % template.name
        template.run(output_dir, vars, verbosity=self.verbosity, overwrite=overwrite)
    
    def display_vars(self, vars, file=sys.stdout):
        vars = sorted(vars.items())
        file.write('Variables:\n')
        if not vars:
            return
        max_length = max([len(name) for name, value in vars])
        for name, value in vars:
            file.write('  %s:%s  %s\n' % (name, ' ' * (max_length - len(name)), value))
    
    def list_templates(self, file=sys.stdout):
        templates = Template.get_templates()
        if not templates:
            file.write('No templates registered.\n')
            return
        template_names = sorted(templates.keys())
        max_length = max([len(name) for name in template_names])
        file.write('Available templates:\n')
        for name in template_names:
            file.write('  %s:%s  %s\n' % (name, 
                                          ' ' * (max_length - len(name)), 
                                          templates[name].summary))
