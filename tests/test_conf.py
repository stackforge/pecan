from unittest import TestCase
from pecan import configuration

class TestConf(TestCase):

    def setUp(self):
        import sys
        import os 

        test_config_d = os.path.join(os.path.dirname(__file__), 'test_config')

        if test_config_d not in sys.path:
            sys.path.append(test_config_d)


    def test_update_config_fail_identifier(self):
        """Fail when naming does not pass correctness"""
        bad_dict = {'bad name':'value'}
        self.assertRaises(ValueError, configuration.Config, bad_dict)

    def test_update_set_config(self):
        """Update an empty configuration with the default values"""

        conf = configuration.initconf()
        conf.update_with_module('config')

        self.assertTrue(conf.app.debug)
        self.assertEqual(conf.app.root, None)
        self.assertEqual(conf.app.template_path, 'myproject/templates')
        self.assertEqual(conf.app.static_root, 'public')

        self.assertEqual(conf.server.host, '1.1.1.1')
        self.assertEqual(conf.server.port, '8081')


    def test_update_set_default_config(self):
        """Update an empty configuration with the default values"""

        conf = configuration.initconf()
        conf.update_with_module('empty')

        self.assertFalse(conf.app.debug)
        self.assertEqual(conf.app.root, None)
        self.assertEqual(conf.app.template_path, '')
        self.assertEqual(conf.app.static_root, 'public')

        self.assertEqual(conf.server.host, '0.0.0.0')
        self.assertEqual(conf.server.port, '8080')


