import pkg_resources
import argparse
import logging
import sys
from warnings import warn

import six

log = logging.getLogger(__name__)


class HelpfulArgumentParser(argparse.ArgumentParser):

    def error(self, message):  # pragma: nocover
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.

        If you override this in a subclass, it should not return -- it
        should either exit or raise an exception.
        """
        self.print_help(sys.stderr)
        self._print_message('\n')
        self.exit(2, '%s: %s\n' % (self.prog, message))


class CommandManager(object):
    """ Used to discover `pecan.command` entry points. """

    def __init__(self):
        self.commands = {}
        self.load_commands()

    def load_commands(self):
        for ep in pkg_resources.iter_entry_points('pecan.command'):
            log.debug('%s loading plugin %s', self.__class__.__name__, ep)
            if ep.name in self.commands:
                warn(
                    "Duplicate entry points found on `%s` - ignoring %s" % (
                        ep.name,
                        ep
                    ),
                    RuntimeWarning
                )
                continue
            try:
                cmd = ep.load()
                cmd.run  # ensure existance; catch AttributeError otherwise
            except Exception as e:  # pragma: nocover
                warn("Unable to load plugin %s: %s" % (ep, e), RuntimeWarning)
                continue
            self.add({ep.name: cmd})

    def add(self, cmd):
        self.commands.update(cmd)


class CommandRunner(object):
    """ Dispatches `pecan` command execution requests. """

    def __init__(self):
        self.manager = CommandManager()
        self.parser = HelpfulArgumentParser(add_help=True)
        self.parser.add_argument(
            '--version',
            action='version',
            version='Pecan %s' % self.version
        )
        self.parse_sub_commands()

    def parse_sub_commands(self):
        subparsers = self.parser.add_subparsers(
            dest='command_name',
            metavar='command'
        )
        for name, cmd in self.commands.items():
            sub = subparsers.add_parser(
                name,
                help=cmd.summary
            )
            for arg in getattr(cmd, 'arguments', tuple()):
                arg = arg.copy()
                if isinstance(arg.get('name'), six.string_types):
                    sub.add_argument(arg.pop('name'), **arg)
                elif isinstance(arg.get('name'), list):
                    sub.add_argument(*arg.pop('name'), **arg)

    def run(self, args):
        ns = self.parser.parse_args(args)
        self.commands[ns.command_name]().run(ns)

    @classmethod
    def handle_command_line(cls):  # pragma: nocover
        runner = CommandRunner()
        runner.run(sys.argv[1:])

    @property
    def version(self):
        return pkg_resources.get_distribution('pecan').version

    @property
    def commands(self):
        return self.manager.commands


class BaseCommandMeta(type):

    @property
    def summary(cls):
        """
        This is used to populate the --help argument on the command line.

        This provides a default behavior which takes the first sentence of the
        command's docstring and uses it.
        """
        return cls.__doc__.strip().splitlines()[0].rstrip('.')


class BaseCommandParent(object):
    """
    A base interface for Pecan commands.

    Can be extended to support ``pecan`` command extensions in individual Pecan
    projects, e.g.,

    $ ``pecan my-custom-command config.py``

    ::

        # myapp/myapp/custom_command.py
        class CustomCommand(pecan.commands.base.BaseCommand):
            '''
            (First) line of the docstring is used to summarize the command.
            '''

            arguments = ({
                'name': '--extra_arg',
                'help': 'an extra command line argument',
                'optional': True
            })

            def run(self, args):
                super(SomeCommand, self).run(args)
                if args.extra_arg:
                    pass
    """

    arguments = ({
        'name': 'config_file',
        'help': 'a Pecan configuration file',
        'nargs': '?',
        'default': None,
    },)

    def run(self, args):
        """To be implemented by subclasses."""
        self.args = args

    def load_app(self):
        from pecan import load_app
        return load_app(self.args.config_file)

BaseCommand = BaseCommandMeta('BaseCommand', (BaseCommandParent,), {
    '__doc__': BaseCommandParent.__doc__
})
