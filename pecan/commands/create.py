"""
Create command for Pecan
"""
from pecan.commands import BaseCommand
from pecan.scaffolds import DEFAULT_SCAFFOLD, BaseScaffold


class CreateCommand(BaseCommand):
    """
    Creates the file layout for a new Pecan scaffolded project.
    """

    arguments = ({
        'command': 'destination',
        'help': 'the destination to create the new project'
    }, {
        'command': 'template_name',
        'help': 'a registered Pecan template',
        'nargs': '?',
        'default': DEFAULT_SCAFFOLD
    })

    def run(self, args):
        super(CreateCommand, self).run(args)
        BaseScaffold().copy_to(args.destination)
