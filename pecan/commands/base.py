"""
PasteScript base command for Pecan.
"""
from pecan.configuration import _runtime_conf, set_config
from paste.script import command as paste_command

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
    
    def can_import(self, name):
        try:
            __import__(name)
            return True
        except ImportError:
            return False
    
    def get_package_names(self, config):
        if not hasattr(config.app, 'modules'):
            return []
        return [module.__name__ for module in config.app.modules if hasattr(module, '__name__')]
    
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
        raise paste_command.BadCommand('No app.setup_app found in any of the configured app.modules')
    
    def load_model(self, config):
        for package_name in self.get_package_names(config):
            module_name = '%s.model' % package_name
            if self.can_import(module_name):
                return sys.modules[module_name]
        return None
    
    def command(self):
        pass

