"""
PasteScript base command for Pecan.
"""
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
    
    def get_package_names(self, config):
        if not hasattr(config.app, 'modules'):
            return []
        return [module.__name__ for module in config.app.modules if hasattr(module, '__name__')]
    
    def import_module(self, package, name):
        parent = __import__(package, fromlist=[name])
        return getattr(parent, name, None)
    
    def load_configuration(self, name):
        set_config(name)
        return _runtime_conf
    
    def load_app(self, config):
        for package_name in self.get_package_names(config):
            module = self.import_module(package_name, 'app')
            if hasattr(module, 'setup_app'):
                return module.setup_app(config)
        raise paste_command.BadCommand('No app.setup_app found in any app modules')
    
    def load_model(self, config):
        for package_name in self.get_package_names(config):
            module = self.import_module(package_name, 'model')
            if module:
                return module
        return None
    
    def logging_file_config(self, config_file):
        if os.path.splitext(config_file)[1].lower() == '.ini':
            paste_command.Command.logging_file_config(self, config_file)
    
    def command(self):
        pass
