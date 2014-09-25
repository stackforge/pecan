"""
Create command for Pecan
"""
import pkg_resources
import logging
from warnings import warn
from pecan.commands import BaseCommand
from pecan.scaffolds import DEFAULT_SCAFFOLD

log = logging.getLogger(__name__)


class ScaffoldManager(object):
    """ Used to discover `pecan.scaffold` entry points. """

    def __init__(self):
        self.scaffolds = {}
        self.load_scaffolds()

    def load_scaffolds(self):
        for ep in pkg_resources.iter_entry_points('pecan.scaffold'):
            log.debug('%s loading scaffold %s', self.__class__.__name__, ep)
            try:
                cmd = ep.load()
                cmd.copy_to  # ensure existance; catch AttributeError otherwise
            except Exception as e:  # pragma: nocover
                warn(
                    "Unable to load scaffold %s: %s" % (ep, e), RuntimeWarning
                )
                continue
            self.add({ep.name: cmd})

    def add(self, cmd):
        self.scaffolds.update(cmd)


class CreateCommand(BaseCommand):
    """
    Creates the file layout for a new Pecan scaffolded project.
    """

    manager = ScaffoldManager()

    arguments = ({
        'name': 'project_name',
        'help': 'the (package) name of the new project'
    }, {
        'name': 'template_name',
        'metavar': 'template_name',
        'help': 'a registered Pecan template',
        'nargs': '?',
        'default': DEFAULT_SCAFFOLD,
        'choices': manager.scaffolds.keys()
    })

    def run(self, args):
        super(CreateCommand, self).run(args)
        self.manager.scaffolds[args.template_name]().copy_to(
            args.project_name
        )
