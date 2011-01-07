"""
PasteScript commands for Pecan.
"""
from paste.script.create_distro import CreateDistroCommand

from pecan.templates import DEFAULT_TEMPLATE
from base import Command

import copy
import os
import sys

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
