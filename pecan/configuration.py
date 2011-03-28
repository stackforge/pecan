import copy
import re
import inspect
import os


IDENTIFIER = re.compile(r'[a-z_](\w)*$', re.IGNORECASE)

class ConfigDict(dict):
    pass

class Config(object):
    '''
    Base class for Pecan configurations.
    '''
    
    def __init__(self, conf_dict={}, filename=''):
        '''
        Create a Pecan configuration object from a dictionary or a 
        filename.
        
        :param conf_dict: A python dictionary to use for the configuration.
        :param filename: A filename to use for the configuration.
        '''
        
        self.__values__ = {}
        self.__file__ = filename
        self.update(conf_dict)

    def update(self, conf_dict):
        '''
        Updates this configuration with a dictionary.
        
        :param conf_dict: A python dictionary to update this configuration with.
        '''
        
        if isinstance(conf_dict, dict):
            iterator = conf_dict.iteritems()
        else:
            iterator = iter(conf_dict)
            
        for k,v in iterator:
            if not IDENTIFIER.match(k):
                raise ValueError('\'%s\' is not a valid indentifier' % k)

            cur_val = self.__values__.get(k)

            if isinstance(cur_val, Config):
                cur_val.update(conf_dict[k])
            else:
                self[k] = conf_dict[k]


    def __dictify__(self, obj, prefix):
        '''
        Private helper method for as_dict.
        Do not use directly.
        '''
        for k, v in obj.items():
            if prefix:
                k = "%s%s" % (prefix, k)
            if isinstance(v, Config):
                v = self.__dictify__(dict(v), prefix)
            obj[k] = v
        return obj


    def as_dict(self, prefix=None):
        '''
        Converts recursively the Config object into a valid dictionary.
        
        :param prefix: A string to optionally prefix key elements in the dict.
        '''
        
        conf_obj = dict(copy.deepcopy(self))
        return self.__dictify__(conf_obj, prefix)


    def update_with_module(self, module):
        '''
        Updates this configuration with a module.
        
        :param module: The module to update this configuration with. Either a string or the module itself.
        '''
        
        self.update(conf_from_module(module))

    def __getattr__(self, name):
        try:
            return self.__values__[name]
        except KeyError:
            raise AttributeError, "'pecan.conf' object has no attribute '%s'" % name

    def __getitem__(self, key):
        return self.__values__[key]

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, ConfigDict):
            if value.get('__force_dict__'):
                del value['__force_dict__']
                self.__values__[key] = ConfigDict(value)
            else:
                self.__values__[key] = Config(value, filename=self.__file__)
        elif isinstance(value, basestring) and '%(confdir)s' in value:
            confdir = os.path.dirname(self.__file__) or os.getcwd()
            self.__values__[key] = value.replace('%(confdir)s', confdir)
        else:
            self.__values__[key] = value

    def __iter__(self):
        return self.__values__.iteritems()

    def __dir__(self):
        """
        When using dir() returns a list of the values in the config.  Note: This function only works in Python2.6 or later.
        """
        return self.__values__.keys()

    def __repr__(self):
        return 'Config(%s)' % str(self.__values__)

def conf_from_module(module):
    '''
    Creates a configuration dictionary from a module.
    
    :param module: The module, either as a string or the module itself.
    '''
    
    if isinstance(module, str):
        module = import_module(module)

    module_dict = dict(inspect.getmembers(module))

    return conf_from_dict(module_dict)


def conf_from_file(filepath):
    '''
    Creates a configuration dictionary from a file.
    
    :param filepath: The path to the file.
    '''
    
    abspath = os.path.abspath(os.path.expanduser(filepath))
    conf_dict = {}

    execfile(abspath, globals(), conf_dict)
    conf_dict['__file__'] = abspath

    return conf_from_dict(conf_dict)


def conf_from_dict(conf_dict):
    '''
    Creates a configuration dictionary from a dictionary.
    
    :param conf_dict: The configuration dictionary.
    '''
    
    conf = Config(filename=conf_dict.get('__file__', ''))

    for k,v in conf_dict.iteritems():
        if k.startswith('__'):
            continue
        elif inspect.ismodule(v):
            continue
        
        conf[k] = v
    return conf


def import_module(conf):
    '''
    Imports the a configuration as a module.
    
    :param conf: The string to the configuration. Automatically strips off ".py" file extensions.
    '''
    
    if conf.endswith('.py'):
        conf = conf[:-3]
    
    if '.' in conf:
        parts = conf.split('.')
        name = '.'.join(parts[:-1])
        fromlist = parts[-1:]

        try:
            module = __import__(name, fromlist=fromlist)
            conf_mod = getattr(module, parts[-1])
        except AttributeError, e:
            raise ImportError('No module named %s' % conf)
    else:
        conf_mod =  __import__(conf)

    return conf_mod


def initconf():
    '''
    Initializes the default configuration and exposes it at ``pecan.configuration.conf``,
    which is also exposed at ``pecan.conf``.
    '''
    
    import default_config
    conf = conf_from_module(default_config)
    return conf


def set_config(name):
    '''
    Updates the global configuration from a path or filename.
    
    :param name: Path or filename, as a string.
    '''
    
    if '/' in name:
        _runtime_conf.update(conf_from_file(name))
    else:
        _runtime_conf.update_with_module(name)


_runtime_conf = initconf()

