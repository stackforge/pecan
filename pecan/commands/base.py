"""
PasteScript base command for Pecan.
"""
from pecan import load_app
from pecan.configuration import _runtime_conf, set_config
from paste.script import command as paste_command

import os.path
import sys


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

    def load_app(self):
        return load_app(self.validate_file(self.args))
    
    def logging_file_config(self, config_file):
        if os.path.splitext(config_file)[1].lower() == '.ini':
            paste_command.Command.logging_file_config(self, config_file)

    def validate_file(self, argv):
        if not argv or not os.path.isfile(argv[0]):
            raise paste_command.BadCommand('This command needs a valid config file.')
        return argv[0]
    
    def command(self):
        pass
