import os
import sys
from unittest import TestCase
from pecan import configuration
from pecan import conf as _runtime_conf

__here__ = os.path.dirname(__file__)


class TestConf(TestCase):

    def test_update_config_fail_identifier(self):
        """Fail when naming does not pass correctness"""
        bad_dict = {'bad name': 'value'}
        self.assertRaises(ValueError, configuration.Config, bad_dict)

    def test_update_set_config(self):
        """Update an empty configuration with the default values"""

        conf = configuration.initconf()
        conf.update(configuration.conf_from_file(os.path.join(
            __here__,
            'test_config/config.py'
        )))

        self.assertTrue(conf.app.debug)
        self.assertEqual(conf.app.root, None)
        self.assertEqual(conf.app.template_path, 'myproject/templates')
        self.assertEqual(conf.app.static_root, 'public')

        self.assertEqual(conf.server.host, '1.1.1.1')
        self.assertEqual(conf.server.port, '8081')

    def test_update_set_default_config(self):
        """Update an empty configuration with the default values"""

        conf = configuration.initconf()
        conf.update(configuration.conf_from_file(os.path.join(
            __here__,
            'test_config/empty.py'
        )))

        self.assertFalse(conf.app.debug)
        self.assertEqual(conf.app.root, None)
        self.assertEqual(conf.app.template_path, '')
        self.assertEqual(conf.app.static_root, 'public')

        self.assertEqual(conf.server.host, '0.0.0.0')
        self.assertEqual(conf.server.port, '8080')

    def test_update_force_dict(self):
        """Update an empty configuration with the default values"""
        conf = configuration.initconf()
        conf.update(configuration.conf_from_file(os.path.join(
            __here__,
            'test_config/forcedict.py'
        )))

        self.assertFalse(conf.app.debug)
        self.assertEqual(conf.app.root, None)
        self.assertEqual(conf.app.template_path, '')
        self.assertEqual(conf.app.static_root, 'public')

        self.assertEqual(conf.server.host, '0.0.0.0')
        self.assertEqual(conf.server.port, '8080')

        self.assertTrue(isinstance(conf.beaker, dict))
        self.assertEqual(conf.beaker['session.key'], 'key')
        self.assertEqual(conf.beaker['session.type'], 'cookie')
        self.assertEqual(
            conf.beaker['session.validate_key'],
            '1a971a7df182df3e1dec0af7c6913ec7'
        )
        self.assertEqual(conf.beaker.get('__force_dict__'), None)

    def test_update_config_with_dict(self):
        conf = configuration.initconf()
        d = {'attr': True}
        conf['attr'] = d
        self.assertTrue(conf.attr.attr)

    def test_config_repr(self):
        conf = configuration.Config({'a': 1})
        self.assertEqual(repr(conf), "Config({'a': 1})")

    def test_config_from_dict(self):
        conf = configuration.conf_from_dict({})
        conf['path'] = '%(confdir)s'
        self.assertTrue(os.path.samefile(conf['path'], os.getcwd()))

    def test_config_from_file(self):
        path = os.path.join(
            os.path.dirname(__file__), 'test_config', 'config.py'
        )
        conf = configuration.conf_from_file(path)
        self.assertTrue(conf.app.debug)

    def test_config_illegal_ids(self):
        conf = configuration.Config({})
        conf.update(configuration.conf_from_file(os.path.join(
            __here__,
            'test_config/bad/module_and_underscore.py'
        )))
        self.assertEqual([], list(conf))

    def test_config_missing_file(self):
        path = ('doesnotexist.py',)
        configuration.Config({})
        self.assertRaises(IOError, configuration.conf_from_file, os.path.join(
            __here__,
            'test_config',
            *path
        ))

    def test_config_missing_file_on_path(self):
        path = ('bad', 'bad', 'doesnotexist.py',)
        configuration.Config({})

        self.assertRaises(IOError, configuration.conf_from_file, os.path.join(
            __here__,
            'test_config',
            *path
        ))

    def test_config_with_syntax_error(self):
        path = ('bad', 'syntaxerror.py')
        configuration.Config({})

        self.assertRaises(
            SyntaxError,
            configuration.conf_from_file,
            os.path.join(__here__, 'test_config', *path)
        )

    def test_config_with_bad_import(self):
        path = ('bad', 'importerror.py')
        configuration.Config({})

        self.assertRaises(
            ImportError,
            configuration.conf_from_file,
            os.path.join(
                __here__,
                'test_config',
                *path
            )
        )

    def test_config_set_from_file(self):
        path = os.path.join(
            os.path.dirname(__file__), 'test_config', 'empty.py'
        )
        configuration.set_config(path)
        res = list(configuration.initconf().server)
        assert list(_runtime_conf.server) == res

    def test_config_dir(self):
        if sys.version_info >= (2, 6):
            conf = configuration.Config({})
            self.assertEqual([], dir(conf))
            conf = configuration.Config({'a': 1})
            self.assertEqual(['a'], dir(conf))

    def test_config_bad_key(self):
        conf = configuration.Config({'a': 1})
        assert conf.a == 1
        self.assertRaises(AttributeError, getattr, conf, 'b')

    def test_config_get_valid_key(self):
        conf = configuration.Config({'a': 1})
        assert conf.get('a') == 1

    def test_config_get_invalid_key(self):
        conf = configuration.Config({'a': 1})
        assert conf.get('b') is None

    def test_config_get_invalid_key_return_default(self):
        conf = configuration.Config({'a': 1})
        assert conf.get('b', True) is True

    def test_config_as_dict(self):
        conf = configuration.initconf()

        assert isinstance(conf, configuration.Config)

        as_dict = conf.as_dict()

        assert isinstance(as_dict, dict)
        assert as_dict['server']['host'] == '0.0.0.0'
        assert as_dict['server']['port'] == '8080'
        assert as_dict['app']['debug'] == False
        assert as_dict['app']['errors'] == {}
        assert as_dict['app']['force_canonical'] == True
        assert as_dict['app']['modules'] == []
        assert as_dict['app']['root'] == None
        assert as_dict['app']['static_root'] == 'public'
        assert as_dict['app']['template_path'] == ''

    def test_config_as_dict_nested(self):
        """have more than one level nesting and convert to dict"""
        conf = configuration.initconf()
        nested = {'one': {'two': 2}}
        conf['nested'] = nested

        as_dict = conf.as_dict()

        assert isinstance(as_dict, dict)
        assert as_dict['server']['host'] == '0.0.0.0'
        assert as_dict['server']['port'] == '8080'
        assert as_dict['app']['debug'] == False
        assert as_dict['app']['errors'] == {}
        assert as_dict['app']['force_canonical'] == True
        assert as_dict['app']['modules'] == []
        assert as_dict['app']['root'] == None
        assert as_dict['app']['static_root'] == 'public'
        assert as_dict['app']['template_path'] == ''
        assert as_dict['nested']['one']['two'] == 2

    def test_config_as_dict_prefixed(self):
        """Add a prefix for keys"""
        conf = configuration.initconf()

        assert isinstance(conf, configuration.Config)

        as_dict = conf.as_dict('prefix_')

        assert isinstance(as_dict, dict)
        assert as_dict['prefix_server']['prefix_host'] == '0.0.0.0'
        assert as_dict['prefix_server']['prefix_port'] == '8080'
        assert as_dict['prefix_app']['prefix_debug'] == False
        assert as_dict['prefix_app']['prefix_errors'] == {}
        assert as_dict['prefix_app']['prefix_force_canonical'] == True
        assert as_dict['prefix_app']['prefix_modules'] == []
        assert as_dict['prefix_app']['prefix_root'] == None
        assert as_dict['prefix_app']['prefix_static_root'] == 'public'
        assert as_dict['prefix_app']['prefix_template_path'] == ''
