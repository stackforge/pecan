"""
PasteScript command runner.
"""
from paste.script import command as paste_command

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
