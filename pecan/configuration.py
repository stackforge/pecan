import re
import inspect
import os
import string


IDENTIFIER = re.compile(r'[a-z_](\w)*$', re.IGNORECASE)

class ConfigDict(dict):
    pass

class Config(object):
    def __init__(self, conf_dict={}, dirname=None):
        self.dirname = dirname or os.getcwd()
        self.update(conf_dict)

    def update(self, conf_dict):
        if isinstance(conf_dict, dict):
            iterator = conf_dict.iteritems()
        else:
            iterator = iter(conf_dict)
            
        for k,v in iterator:
            if not IDENTIFIER.match(k):
                raise ValueError('\'%s\' is not a valid indentifier' % k)

            cur_val = self.__dict__.get(k)

            if isinstance(cur_val, Config):
                cur_val.update(conf_dict[k])
            else:
                self[k] = conf_dict[k]

    def update_with_module(self, module):
        self.update(conf_from_module(module))

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, ConfigDict):
            if value.get('__force_dict__'):
                del value['__force_dict__']
                self.__dict__[key] = ConfigDict(value)
            else:
                self.__dict__[key] = Config(value, dirname=self.dirname)
        elif isinstance(value, basestring) and '%(confdir)s' in value:
            self.__dict__[key] = value.replace('%(confdir)s', self.dirname)
        else:
            self.__dict__[key] = value

    def __iter__(self):
        return self.__dict__.iteritems()

    def __dir__(self):
        return self.__dict__.keys()

    def __repr__(self):
        return 'Config(%s)' % str(self.__dict__)

def conf_from_module(module):
    if isinstance(module, str):
        module = import_module(module)

    module_dict = dict(inspect.getmembers(module))

    return conf_from_dict(module_dict)


def conf_from_file(filepath):
    abspath = os.path.abspath(os.path.expanduser(filepath))
    conf_dict = {}

    execfile(abspath, globals(), conf_dict)
    conf_dict['__file__'] = abspath

    return conf_from_dict(conf_dict)


def conf_from_dict(conf_dict):

    # set the configdir
    dirname = os.path.dirname(conf_dict.get('__file__', ''))
    if dirname == '':
        dirname = os.getcwd()

    conf = Config(dirname=dirname)

    for k,v in conf_dict.iteritems():
        if k.startswith('__'):
            continue
        elif inspect.ismodule(v):
            continue
        
        conf[k] = v
    return conf


def import_module(conf):
    if conf.endswith('.py'):
        conf = conf[:-3]
    
    if '.' in conf:
        parts = conf.split('.')
        name = '.'.join(parts[:-1])
        fromlist = parts[-1:]

        try:
            module = __import__(name, fromlist=fromlist)
            conf_mod = getattr(module, parts[-1])
        except ImportError, e:
            raise ImportError('No module named %s' % conf)
        except AttributeError, e:
            raise ImportError('No module named %s' % conf)
    else:
        name = conf

        try:
            conf_mod =  __import__(name)
        except ImportError, e:
            raise ImportError('No module named %s' % conf)

    return conf_mod


def initconf():
    import default_config
    conf = conf_from_module(default_config)
    return conf


def set_config(name):
    if '/' in name:
        _runtime_conf.update(conf_from_file(name))
    else:
        _runtime_conf.update_with_module(name)


_runtime_conf = initconf()

