import re
import inspect

IDENTIFIER = re.compile('[A-Za-z_]([A-Za-z0-9_])*$')


class Config(object):
    def __init__(self, conf_dict={}):
        self.update(conf_dict)

    def update(self, conf_dict):
        # first check the keys for correct
        for k in conf_dict:
            if not IDENTIFIER.match(k):
                raise ValueError('\'%s\' is not a valid indentifier' % k)

            cur_val = self.__dict__.get(k)

            if isinstance(cur_val, Config):
                cur_val.update(conf_dict[k])
            else:
                self.__dict__[k] = conf_dict[k]

    def update_with_module(self, module):
        self.update(conf_from_module(module))

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __iter__(self):
        return self.__dict__.__iter__()

    def __dir__(self):
        return self.__dict__.keys()

    def __repr__(self):
        return 'Config(%s)' % str(self.__dict__)

def initconf():
    import default_config
    return conf_from_module(default_config)

def conf_from_module(module):
    if isinstance(module, str):
        module = import_runtime_conf(module)

    conf = Config()

    for k,v in inspect.getmembers(module):
        if k.startswith('__'):
            continue
        
        if isinstance(v, dict):
            conf[k] = Config(v)
        else:
            conf[k] = v
    return conf

def import_runtime_conf(conf):
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
