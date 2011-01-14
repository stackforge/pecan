import os
from unittest import TestCase
from pecan import configuration
from pecan import conf as _runtime_conf

class TestConf(TestCase):

    def setUp(self):
        import sys

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
        
    def test_update_force_dict(self):
        """Update an empty configuration with the default values"""

        conf = configuration.initconf()
        conf.update_with_module('forcedict')

        self.assertFalse(conf.app.debug)
        self.assertEqual(conf.app.root, None)
        self.assertEqual(conf.app.template_path, '')
        self.assertEqual(conf.app.static_root, 'public')

        self.assertEqual(conf.server.host, '0.0.0.0')
        self.assertEqual(conf.server.port, '8080')

        self.assertEqual(type(conf.beaker), dict)
        self.assertEqual(conf.beaker['session.key'], 'key')
        self.assertEqual(conf.beaker['session.type'], 'cookie')
        self.assertEqual(conf.beaker['session.validate_key'], '1a971a7df182df3e1dec0af7c6913ec7')
        self.assertTrue(conf.beaker.get('__force_dict__'), None)

    def test_update_config_fail_bad_attribute(self):
        conf = configuration.initconf()
        self.assertRaises(AttributeError, conf.update_with_module, 'bad.attribute')
    def test_update_config_with_dict(self):
        conf = configuration.initconf()
        d = {'attr':True}
        conf['attr'] = d
        self.assertTrue(conf.attr.attr)

    def test_module_ends_in_py(self):
        conf = configuration.initconf()
        conf.update_with_module('config.py')

    def test_config_dir(self):
        conf = configuration.initconf()

        self.assertTrue('__confdir__' in dir(conf))

    def test_config_file(self):
        conf = configuration.initconf()

        self.assertTrue('__conffile__' in dir(conf))

    def test_config_repr(self):
        conf = configuration.Config({'a':1})
        self.assertEqual(repr(conf),"Config({'a': 1})")

    def test_config_from_dict(self):
        conf = configuration.conf_from_dict({})
        self.assertTrue(os.path.samefile(conf.__confdir__, os.getcwd()))

    def test_config_from_file(self):
        path = os.path.join(os.path.dirname(__file__), 'test_config', 'config.py')
        conf = configuration.conf_from_file(path)
        self.assertTrue(conf.app.debug)

    def test_config_illegal_ids(self):
        conf = configuration.Config({})
        conf.update_with_module('bad.module_and_underscore')
        self.assertEqual(['__confdir__', '__conffile__'], dir(conf))

    def test_config_bad_module(self):
        conf = configuration.Config({})
        self.assertRaises(ImportError, conf.update_with_module, 'doesnotexist')
        self.assertRaises(ImportError, conf.update_with_module, 'bad.doesnotexists')
        self.assertRaises(ImportError, conf.update_with_module, 'bad.bad.doesnotexist')

    def test_config_set_from_file(self):
        path = os.path.join(os.path.dirname(__file__), 'test_config', 'empty.py')
        configuration.set_config(path)
        self.assertTrue(dir(_runtime_conf.app), [])

    def test_config_set_from_module(self):
        configuration.set_config('config')
        self.assertEqual(_runtime_conf.server.host, '1.1.1.1')


    def test_config_string(self):
        s = '{pecan.conf.app}'
        self.assertTrue(configuration.ConfigString.contains_formatting(s))
        cs = configuration.ConfigString(s)
        self.assertEqual(str(cs), s)

