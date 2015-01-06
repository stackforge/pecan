import os
import sys
import tempfile

from pecan.tests import PecanTestCase
from six import b as b_


__here__ = os.path.dirname(__file__)


class TestConf(PecanTestCase):

    def test_update_config_fail_identifier(self):
        """Fail when naming does not pass correctness"""
        from pecan import configuration
        bad_dict = {'bad name': 'value'}
        self.assertRaises(ValueError, configuration.Config, bad_dict)

    def test_update_set_config(self):
        """Update an empty configuration with the default values"""
        from pecan import configuration

        conf = configuration.initconf()
        conf.update(configuration.conf_from_file(os.path.join(
            __here__,
            'config_fixtures/config.py'
        )))

        self.assertEqual(conf.app.root, None)
        self.assertEqual(conf.app.template_path, 'myproject/templates')
        self.assertEqual(conf.app.static_root, 'public')

        self.assertEqual(conf.server.host, '1.1.1.1')
        self.assertEqual(conf.server.port, '8081')

    def test_update_set_default_config(self):
        """Update an empty configuration with the default values"""
        from pecan import configuration

        conf = configuration.initconf()
        conf.update(configuration.conf_from_file(os.path.join(
            __here__,
            'config_fixtures/empty.py'
        )))

        self.assertEqual(conf.app.root, None)
        self.assertEqual(conf.app.template_path, '')
        self.assertEqual(conf.app.static_root, 'public')

        self.assertEqual(conf.server.host, '0.0.0.0')
        self.assertEqual(conf.server.port, '8080')

    def test_update_force_dict(self):
        """Update an empty configuration with the default values"""
        from pecan import configuration
        conf = configuration.initconf()
        conf.update(configuration.conf_from_file(os.path.join(
            __here__,
            'config_fixtures/forcedict.py'
        )))

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
        from pecan import configuration
        conf = configuration.initconf()
        d = {'attr': True}
        conf['attr'] = d
        self.assertTrue(conf.attr.attr)

    def test_config_repr(self):
        from pecan import configuration
        conf = configuration.Config({'a': 1})
        self.assertEqual(repr(conf), "Config({'a': 1})")

    def test_config_from_dict(self):
        from pecan import configuration
        conf = configuration.conf_from_dict({})
        conf['path'] = '%(confdir)s'
        self.assertTrue(os.path.samefile(conf['path'], os.getcwd()))

    def test_config_from_file(self):
        from pecan import configuration
        path = os.path.join(
            os.path.dirname(__file__), 'config_fixtures', 'config.py'
        )
        configuration.conf_from_file(path)

    def test_config_illegal_ids(self):
        from pecan import configuration
        conf = configuration.Config({})
        conf.update(configuration.conf_from_file(os.path.join(
            __here__,
            'config_fixtures/bad/module_and_underscore.py'
        )))
        self.assertEqual([], list(conf))

    def test_config_missing_file(self):
        from pecan import configuration
        path = ('doesnotexist.py',)
        configuration.Config({})
        self.assertRaises(
            RuntimeError,
            configuration.conf_from_file,
            os.path.join(__here__, 'config_fixtures', *path)
        )

    def test_config_missing_file_on_path(self):
        from pecan import configuration
        path = ('bad', 'bad', 'doesnotexist.py',)
        configuration.Config({})

        self.assertRaises(
            RuntimeError,
            configuration.conf_from_file,
            os.path.join(__here__, 'config_fixtures', *path)
        )

    def test_config_with_syntax_error(self):
        from pecan import configuration
        with tempfile.NamedTemporaryFile('wb') as f:
            f.write(b_('\n'.join(['if false', 'var = 3'])))
            f.flush()
            configuration.Config({})

            self.assertRaises(
                SyntaxError,
                configuration.conf_from_file,
                f.name
            )

    def test_config_with_non_package_relative_import(self):
        from pecan import configuration
        with tempfile.NamedTemporaryFile('wb', suffix='.py') as f:
            f.write(b_('\n'.join(['from . import variables'])))
            f.flush()
            configuration.Config({})

            try:
                configuration.conf_from_file(f.name)
            except (ValueError, SystemError) as e:
                assert 'relative import' in str(e)
            else:
                raise AssertionError(
                    "A relative import-related error should have been raised"
                )

    def test_config_with_bad_import(self):
        from pecan import configuration
        path = ('bad', 'importerror.py')
        configuration.Config({})

        self.assertRaises(
            ImportError,
            configuration.conf_from_file,
            os.path.join(
                __here__,
                'config_fixtures',
                *path
            )
        )

    def test_config_dir(self):
        from pecan import configuration
        if sys.version_info >= (2, 6):
            conf = configuration.Config({})
            self.assertEqual([], dir(conf))
            conf = configuration.Config({'a': 1})
            self.assertEqual(['a'], dir(conf))

    def test_config_bad_key(self):
        from pecan import configuration
        conf = configuration.Config({'a': 1})
        assert conf.a == 1
        self.assertRaises(AttributeError, getattr, conf, 'b')

    def test_config_get_valid_key(self):
        from pecan import configuration
        conf = configuration.Config({'a': 1})
        assert conf.get('a') == 1

    def test_config_get_invalid_key(self):
        from pecan import configuration
        conf = configuration.Config({'a': 1})
        assert conf.get('b') is None

    def test_config_get_invalid_key_return_default(self):
        from pecan import configuration
        conf = configuration.Config({'a': 1})
        assert conf.get('b', True) is True

    def test_config_to_dict(self):
        from pecan import configuration
        conf = configuration.initconf()

        assert isinstance(conf, configuration.Config)

        to_dict = conf.to_dict()

        assert isinstance(to_dict, dict)
        assert to_dict['server']['host'] == '0.0.0.0'
        assert to_dict['server']['port'] == '8080'
        assert to_dict['app']['modules'] == []
        assert to_dict['app']['root'] is None
        assert to_dict['app']['static_root'] == 'public'
        assert to_dict['app']['template_path'] == ''

    def test_config_to_dict_nested(self):
        from pecan import configuration
        """have more than one level nesting and convert to dict"""
        conf = configuration.initconf()
        nested = {'one': {'two': 2}}
        conf['nested'] = nested

        to_dict = conf.to_dict()

        assert isinstance(to_dict, dict)
        assert to_dict['server']['host'] == '0.0.0.0'
        assert to_dict['server']['port'] == '8080'
        assert to_dict['app']['modules'] == []
        assert to_dict['app']['root'] is None
        assert to_dict['app']['static_root'] == 'public'
        assert to_dict['app']['template_path'] == ''
        assert to_dict['nested']['one']['two'] == 2

    def test_config_to_dict_prefixed(self):
        from pecan import configuration
        """Add a prefix for keys"""
        conf = configuration.initconf()

        assert isinstance(conf, configuration.Config)

        to_dict = conf.to_dict('prefix_')

        assert isinstance(to_dict, dict)
        assert to_dict['prefix_server']['prefix_host'] == '0.0.0.0'
        assert to_dict['prefix_server']['prefix_port'] == '8080'
        assert to_dict['prefix_app']['prefix_modules'] == []
        assert to_dict['prefix_app']['prefix_root'] is None
        assert to_dict['prefix_app']['prefix_static_root'] == 'public'
        assert to_dict['prefix_app']['prefix_template_path'] == ''


class TestGlobalConfig(PecanTestCase):

    def tearDown(self):
        from pecan import configuration
        configuration.set_config(
            dict(configuration.initconf()),
            overwrite=True
        )

    def test_paint_from_dict(self):
        from pecan import configuration
        configuration.set_config({'foo': 'bar'})
        assert dict(configuration._runtime_conf) != {'foo': 'bar'}
        self.assertEqual(configuration._runtime_conf.foo, 'bar')

    def test_overwrite_from_dict(self):
        from pecan import configuration
        configuration.set_config({'foo': 'bar'}, overwrite=True)
        assert dict(configuration._runtime_conf) == {'foo': 'bar'}

    def test_paint_from_file(self):
        from pecan import configuration
        configuration.set_config(os.path.join(
            __here__,
            'config_fixtures/foobar.py'
        ))
        assert dict(configuration._runtime_conf) != {'foo': 'bar'}
        assert configuration._runtime_conf.foo == 'bar'

    def test_overwrite_from_file(self):
        from pecan import configuration
        configuration.set_config(
            os.path.join(
                __here__,
                'config_fixtures/foobar.py',
            ),
            overwrite=True
        )
        assert dict(configuration._runtime_conf) == {'foo': 'bar'}

    def test_set_config_none_type(self):
        from pecan import configuration
        self.assertRaises(RuntimeError, configuration.set_config, None)

    def test_set_config_to_dir(self):
        from pecan import configuration
        self.assertRaises(RuntimeError, configuration.set_config, '/')


class TestConfFromEnv(PecanTestCase):
    #
    # Note that there is a good chance of pollution if ``tearDown`` does not
    # reset the configuration like this class does. If implementing new classes
    # for configuration this tearDown **needs to be implemented**
    #

    def setUp(self):
        super(TestConfFromEnv, self).setUp()
        self.addCleanup(self._remove_config_key)

        from pecan import configuration
        self.get_conf_path_from_env = configuration.get_conf_path_from_env

    def _remove_config_key(self):
        os.environ.pop('PECAN_CONFIG', None)

    def test_invalid_path(self):
        os.environ['PECAN_CONFIG'] = '/'
        msg = "PECAN_CONFIG was set to an invalid path: /"
        self.assertRaisesRegexp(
            RuntimeError,
            msg,
            self.get_conf_path_from_env
        )

    def test_is_not_set(self):
        msg = "PECAN_CONFIG is not set and " \
              "no config file was passed as an argument."
        self.assertRaisesRegexp(
            RuntimeError,
            msg,
            self.get_conf_path_from_env
        )

    def test_return_valid_path(self):
        __here__ = os.path.abspath(__file__)
        os.environ['PECAN_CONFIG'] = __here__
        assert self.get_conf_path_from_env() == __here__
