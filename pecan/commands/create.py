"""
Create command for Pecan
"""
from pecan.commands import BaseCommand
from pecan.templates import DEFAULT_TEMPLATE

import copy
import sys


class CreateCommand(BaseCommand):
    """
    Creates the file layout for a new Pecan distribution.

    For a template to show up when using this command, its name must begin
    with "pecan-". Although not required, it should also include the "Pecan"
    egg plugin for user convenience.
    """

    arguments = ({
        'command': 'template_name',
        'help': 'a registered Pecan template',
        'nargs': '?',
        'default': DEFAULT_TEMPLATE
    },)

    def run(self, args):
        super(CreateCommand, self).run(args)
        print "NOT IMPLEMENTED"
        print args.template_name
