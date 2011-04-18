"""
Plugin for py.test that sets up the app.

App configuration inspired by the Pylons nose equivalent:
https://github.com/Pylons/pylons/blob/master/pylons/test.py

Handling of multiprocessing inspired by pytest-cov.
"""
from pecan import conf, set_config
from tempfile import mkdtemp

import py
import py.test
import os
import shutil
import socket
import sys


def pytest_addoption(parser):
    """
    Adds the custom "with-config" option to take in the config file.
    """
    group = parser.getgroup('pecan')
    group._addoption('--with-config', 
                     dest='config_file', 
                     metavar='path', 
                     default='./test.py',
                     action='store', 
                     type='string', 
                     help='configuration file for pecan tests')


def pytest_configure(config):
    """
    Loads the Pecan plugin if using a configuration file.
    """
    if config.getvalue('config_file'):
        config.pluginmanager.register(PecanPlugin(config), '_pecan')


class PecanPlugin(object):
    """
    Plugin for a Pecan application. Sets up and tears down the 
    WSGI application based on the configuration and session type.
    """
    
    def __init__(self, config):
        self.config = config
        self.impl = None
    
    def pytest_namespace(self):
        """
        Add the session variables to the namespace.
        """
        return {
            'temp_dir': None,
            'wsgi_app': None
        }
    
    def pytest_sessionstart(self, session):
        """
        Set up the testing session.
        """
        self.impl = PecanPluginImpl.create_from_session(session)
        self.impl.sessionstart(session)
    
    def pytest_configure_node(self, node):
        """
        Configures a new slave node.
        """
        if self.impl:
            self.impl.configure_node(node)
    
    def pytest_testnodedown(self, node, error):
        """
        Tears down an exiting node.
        """
        if self.impl:
            self.impl.testnodedown(node, error)
    
    def pytest_sessionfinish(self, session, exitstatus):
        """
        Cleans up the testing session.
        """
        if self.impl:
            self.impl.sessionfinish(session, exitstatus)


class PecanPluginImpl(object):
    """
    Actual implementation of the Pecan plugin. This ensures the proper 
    environment is configured for each session type.
    """
    
    def __init__(self, config):
        self.config = config
        self.log = py.log.Producer('pecan-%s' % self.name)
        if not config.option.debug:
            py.log.setconsumer(self.log._keywords, None)
        self.log('Created %s instance' % self.__class__.__name__)
    
    @property
    def name(self):
        return 'main'
    
    def _setup_app(self):
        self.log('Invoking setup_app')
        path = os.getcwd()
        if path not in sys.path:
            sys.path.insert(0, path)
        set_config(self.config.getvalue('config_file'))
        py.test.wsgi_app = self._load_app(conf)
    
    def _get_package_names(self, config):
        if not hasattr(config.app, 'modules'):
            return []
        return [module.__name__ for module in config.app.modules if hasattr(module, '__name__')]
    
    def _can_import(self, name):
        try:
            __import__(name)
            return True
        except ImportError:
            return False
    
    def _load_app(self, config):
        for package_name in self._get_package_names(config):
            module_name = '%s.app' % package_name
            if self._can_import(module_name):
                module = sys.modules[module_name]
                if hasattr(module, 'setup_app'):
                    return module.setup_app(config)
        raise RuntimeError('No app.setup_app found in any of the configured app.modules')
    
    def _create_temp_directory(self):
        temp_dir = mkdtemp()
        self.log('Created temporary directory %s' % temp_dir)
        py.test.temp_dir = temp_dir
    
    def _delete_temp_directory(self):
        if py.test.temp_dir and os.path.exists(py.test.temp_dir):
            self.log('Removing temporary directory %s' % py.test.temp_dir)
            shutil.rmtree(py.test.temp_dir)
    
    def sessionstart(self, session):
        self.log('Starting session')
        self._setup_app()
        self._create_temp_directory()
    
    def configure_node(self, node):
        pass
    
    def testnodedown(self, node, error):
        pass
    
    def sessionfinish(self, session, exitstatus):
        self.log('Stopping session')
        self._delete_temp_directory()
    
    @staticmethod
    def create_from_session(session):
        if session.config.option.dist != 'no':
            impl_cls = MasterPecanPluginImpl
        elif getattr(session.config, 'slaveinput', {}).get('slaveid'):
            impl_cls = SlavePecanPluginImpl
        else:
            impl_cls = PecanPluginImpl
        return impl_cls(session.config)


class MasterPecanPluginImpl(PecanPluginImpl):
    """
    Plugin implementation for distributed master.
    """
    
    def sessionstart(self, session):
        self.log('Starting master session')
        self._setup_app()
        self._create_temp_directory()
    
    def configure_node(self, node):
        self.log('Configuring slave node %s' % node.gateway.id)
        node.slaveinput['pecan_master_host'] = socket.gethostname()
        node.slaveinput['pecan_temp_dir'] = py.test.temp_dir
    
    def sessionfinish(self, session, exitstatus):
        self.log('Stopping master session')
        self._delete_temp_directory()


class SlavePecanPluginImpl(PecanPluginImpl):
    """
    Plugin implementation for distributed slaves.
    """
    
    @property
    def name(self):
        return self.config.slaveinput['slaveid']
    
    def _is_collocated(self, session):
        return (socket.gethostname() == session.config.slaveinput['pecan_master_host'])
    
    def _set_temp_directory(self, session):
        self.log('Setting temporary directory to %s' % session.config.slaveinput['pecan_temp_dir'])
        py.test.temp_dir = session.config.slaveinput['pecan_temp_dir']
    
    def sessionstart(self, session):
        self.log('Starting slave session')
        self._setup_app()
        if self._is_collocated(session):
            self._set_temp_directory(session)
        else:
            self._create_temp_directory()
    
    def sessionfinish(self, session, exitstatus):
        self.log('Stopping slave session')
        if not self._is_collocated(session):
            self._delete_temp_directory()
