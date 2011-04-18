from unittest import TestCase
import config


class TestConfigServer(TestCase):

    def test_server_port(self):
        assert config.server['port'] == '8080'

    def test_server_host(self):
        assert config.server['host'] == '0.0.0.0'


class TestConfigApp(TestCase):

    def test_app_root(self):
        root = config.app['root']
        assert root.__class__.__name__ == 'RootController'

    def test_app_modules(self):
        assert len(config.app['modules']) == 1
        
    def test_app_static_root(self):
        assert 'public' in config.app['static_root']
        
    def test_app_template_path(self):
        assert 'templates' in config.app['template_path']

    def test_app_reload(self):
        assert config.app['reload'] 

    def test_app_debug(self):
        assert config.app['debug']

    def test_app_errors(self):
        errors = {
            '404' : '/error/404',
            '__force_dict__' : True
        }
        
        assert config.app['errors'] == errors
