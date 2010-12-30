import re
import inspect
import os
import string

IDENTIFIER = re.compile(r'[a-z_](\w)*$', re.IGNORECASE)
STRING_FORMAT = re.compile(r'{pecan\.conf(?P<var>([.][a-z_][\w]*)+)+?}', re.IGNORECASE)

class ConfigString(object):
    def __init__(self, format_string):
        self.raw_string = format_string

    def __call__(self):
        retval = self.raw_string

        for candidate in STRING_FORMAT.finditer(self.raw_string):
            var = candidate.groupdict().get('var','')

            try:
                obj = _runtime_conf
                for dotted_part in var.split('.'):
                    if dotted_part == '':
                        continue
                    obj = getattr(obj, dotted_part)
                
                retval = retval.replace(candidate.group(), str(obj))

            except AttributeError, e:
                raise AttributeError, 'Cannot substitute \'%s\' using the current configuration' % candidate.group()

        return retval

    def __str__(self):
        return self.raw_string

    @staticmethod
    def contains_formatting(value):
        return STRING_FORMAT.match(value)

class Config(object):
    def __init__(self, conf_dict={}):
        self.update(conf_dict)

    def update(self, conf_dict):
        __force_dict__ = False
        # first check the keys for correct

        if isinstance(conf_dict, dict):
            if '__force_dict__' in conf_dict:
                del conf_dict['__force_dict__']
                __force_dict__ = True
            iterator = conf_dict.iteritems()
        else:
            iterator = iter(conf_dict)
            
        for k,v in iterator:
            if not IDENTIFIER.match(k) and not __force_dict__:
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
        if isinstance(value, dict):
            if value.get('__force_dict__'):
                self.__dict__[key] = value
            else:
                self.__dict__[key] = Config(value)
        elif isinstance(value, str) and ConfigString.contains_formatting(value):
            self.__dict__[key] = ConfigString(value)
        else:
            self.__dict__[key] = value

    def __iter__(self):
        return self.__dict__.iteritems()

    def __dir__(self):
        return self.__dict__.keys()

    def __repr__(self):
        return 'Config(%s)' % str(self.__dict__)

    def __call__(self):
        for k,v in self:
            if isinstance(v, Config):
                v()
            elif hasattr(v, '__call__'):
                self.__dict__[k] = v()
        return self



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
    conf = Config()

    # set the configdir
    conf_dir = os.path.dirname(conf_dict.get('__file__', ''))
    if conf_dir == '':
        conf_dir = os.getcwd()

    conf['__confdir__'] = conf_dir + '/'

    for k,v in conf_dict.iteritems():
        if k.startswith('__'):
            continue
        elif inspect.ismodule(v):
            continue
        
        conf[k] = v
    conf()
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
    conf()
    return conf

def set_config(name):
    if '/' in name:
        _runtime_conf.update(conf_from_file(name))
    else:
        _runtime_conf.update_with_module(name)

_runtime_conf = initconf()

