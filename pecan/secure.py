from inspect import getmembers, ismethod, isfunction
from decorators import _cfg

from routing import iscontroller

__all__ = ['Any', 'Protected', 'unlocked', 'secure', 'SecureController'] 

class _Unlocked(object):
    """ 
    A wrapper class to declare a class as unlocked inside of a SecureController
    """
    def __init__(self, obj):
        self.obj = obj


class _SecureState(object):
    def __init__(self, desc, boolean_value):
        self.description = desc
        self.boolean_value = boolean_value
    def __repr__(self):
        return '<SecureState %s>' % self.description
    def __nonzero__(self):
        return self.boolean_value

Any = _SecureState('Any', False)
Protected = _SecureState('Protected', True)

def unlocked(func_or_obj):
    if ismethod(func_or_obj) or isfunction(func_or_obj):
        _cfg(func_or_obj)['secured'] = Any
        return func_or_obj
    else:
        return _Unlocked(func_or_obj)

def secure(check_permissions):
    def wrap(func):
        cfg = _cfg(func)
        cfg['secured'] = Protected
        cfg['check_permissions'] = check_permissions
        return func
    return wrap


class SecureController(object):
    """
    Used to apply security to a controller. 
    Implementations of SecureController should extend the
    `check_permissions` method to return a True or False
    value (depending on whether or not the user has permissions
    to the controller).
    """
    class __metaclass__(type):
        def __init__(cls, name, bases, dict_):
            cls._pecan = dict(secured=Protected, check_permissions=cls.check_permissions, unlocked=[])

            for name, value in getmembers(cls):
                if ismethod(value):
                    if iscontroller(value) and value._pecan.get('secured') is not Any:
                        value._pecan['secured'] = Protected
                        value._pecan['check_permissions'] = cls.check_permissions
                elif hasattr(value, '__class__'):
                    if name.startswith('__') and name.endswith('__'): continue
                    if isinstance(value, _Unlocked):
                        # mark it as unlocked and remove wrapper
                        cls._pecan['unlocked'].append(value.obj)
                        setattr(cls, name, value.obj)

    @classmethod
    def check_permissions(cls):
        return False

