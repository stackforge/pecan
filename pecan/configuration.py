import re
import inspect
import os

import six


IDENTIFIER = re.compile(r'[a-z_](\w)*$', re.IGNORECASE)

DEFAULT = {
    # Server Specific Configurations
    'server': {
        'port': '8080',
        'host': '0.0.0.0'
    },

    # Pecan Application Configurations
    'app': {
        'root': None,
        'modules': [],
        'static_root': 'public',
        'template_path': '',
        'force_canonical': True
    }
}


class ConfigDict(dict):
    pass


class Config(object):
    '''
    Base class for Pecan configurations.

    Create a Pecan configuration object from a dictionary or a
    filename.

    :param conf_dict: A python dictionary to use for the configuration.
    :param filename: A filename to use for the configuration.
    '''

    def __init__(self, conf_dict={}, filename=''):

        self.__values__ = {}
        self.__file__ = filename
        self.update(conf_dict)

    def empty(self):
        self.__values__ = {}

    def update(self, conf_dict):
        '''
        Updates this configuration with a dictionary.

        :param conf_dict: A python dictionary to update this configuration
                          with.
        '''

        if isinstance(conf_dict, dict):
            iterator = six.iteritems(conf_dict)
        else:
            iterator = iter(conf_dict)

        for k, v in iterator:
            if not IDENTIFIER.match(k):
                raise ValueError('\'%s\' is not a valid indentifier' % k)

            cur_val = self.__values__.get(k)

            if isinstance(cur_val, Config):
                cur_val.update(conf_dict[k])
            else:
                self[k] = conf_dict[k]

    def get(self, attribute, default=None):
        try:
            return self[attribute]
        except KeyError:
            return default

    def __dictify__(self, obj, prefix):
        '''
        Private helper method for to_dict.
        '''
        for k, v in obj.copy().items():
            if prefix:
                del obj[k]
                k = "%s%s" % (prefix, k)
            if isinstance(v, Config):
                v = self.__dictify__(dict(v), prefix)
            obj[k] = v
        return obj

    def to_dict(self, prefix=None):
        '''
        Converts recursively the Config object into a valid dictionary.

        :param prefix: A string to optionally prefix all key elements in the
                       returned dictonary.
        '''

        conf_obj = dict(self)
        return self.__dictify__(conf_obj, prefix)

    def __getattr__(self, name):
        try:
            return self.__values__[name]
        except KeyError:
            msg = "'pecan.conf' object has no attribute '%s'" % name
            raise AttributeError(msg)

    def __getitem__(self, key):
        return self.__values__[key]

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, ConfigDict):
            if value.get('__force_dict__'):
                del value['__force_dict__']
                self.__values__[key] = ConfigDict(value)
            else:
                self.__values__[key] = Config(value, filename=self.__file__)
        elif isinstance(value, six.string_types) and '%(confdir)s' in value:
            confdir = os.path.dirname(self.__file__) or os.getcwd()
            self.__values__[key] = value.replace('%(confdir)s', confdir)
        else:
            self.__values__[key] = value

    def __iter__(self):
        return six.iteritems(self.__values__)

    def __dir__(self):
        """
        When using dir() returns a list of the values in the config.  Note:
        This function only works in Python2.6 or later.
        """
        return list(self.__values__.keys())

    def __repr__(self):
        return 'Config(%s)' % str(self.__values__)


def conf_from_file(filepath):
    '''
    Creates a configuration dictionary from a file.

    :param filepath: The path to the file.
    '''

    abspath = os.path.abspath(os.path.expanduser(filepath))
    conf_dict = {}
    if not os.path.isfile(abspath):
        raise RuntimeError('`%s` is not a file.' % abspath)

    with open(abspath, 'rb') as f:
        exec(compile(f.read(), abspath, 'exec'), globals(), conf_dict)
    conf_dict['__file__'] = abspath

    return conf_from_dict(conf_dict)


def get_conf_path_from_env():
    '''
    If the ``PECAN_CONFIG`` environment variable exists and it points to
    a valid path it will return that, otherwise it will raise
    a ``RuntimeError``.
    '''
    config_path = os.environ.get('PECAN_CONFIG')
    if not config_path:
        error = "PECAN_CONFIG is not set and " \
                "no config file was passed as an argument."
    elif not os.path.isfile(config_path):
        error = "PECAN_CONFIG was set to an invalid path: %s" % config_path
    else:
        return config_path

    raise RuntimeError(error)


def conf_from_dict(conf_dict):
    '''
    Creates a configuration dictionary from a dictionary.

    :param conf_dict: The configuration dictionary.
    '''
    conf = Config(filename=conf_dict.get('__file__', ''))

    for k, v in six.iteritems(conf_dict):
        if k.startswith('__'):
            continue
        elif inspect.ismodule(v):
            continue

        conf[k] = v
    return conf


def initconf():
    '''
    Initializes the default configuration and exposes it at
    ``pecan.configuration.conf``, which is also exposed at ``pecan.conf``.
    '''
    return conf_from_dict(DEFAULT)


def set_config(config, overwrite=False):
    '''
    Updates the global configuration.

    :param config: Can be a dictionary containing configuration, or a string
                   which represents a (relative) configuration filename.
    '''

    if config is None:
        config = get_conf_path_from_env()

    # must be after the fallback other a bad fallback will incorrectly clear
    if overwrite is True:
        _runtime_conf.empty()

    if isinstance(config, six.string_types):
        config = conf_from_file(config)
        _runtime_conf.update(config)
        if config.__file__:
            _runtime_conf.__file__ = config.__file__
    elif isinstance(config, dict):
        _runtime_conf.update(conf_from_dict(config))
    else:
        raise TypeError('%s is neither a dictionary or a string.' % config)


_runtime_conf = initconf()
