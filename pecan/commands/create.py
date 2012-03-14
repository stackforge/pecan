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
        'command': 'template_name',
        'help': 'a registered Pecan template',
        'nargs': '?',
        'default': DEFAULT_SCAFFOLD
    },)

    def run(self, args):
        super(CreateCommand, self).run(args)
        print "NOT IMPLEMENTED"
        print args.template_name
        BaseScaffold().copy_to(args.template_name)
