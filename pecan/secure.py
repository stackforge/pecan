from webob.exc import HTTPUnauthorized
from inspect import getmembers, ismethod

from routing import iscontroller


__all__ = ['secure', 'unlocked', 'SecureController']


def unlocked(func):
    if not hasattr(func, 'pecan'): func.pecan = {}
    func.pecan['unlocked'] = True
    return func


def secure(check_permissions):
    def wrap(func):
        if not hasattr(func, 'pecan'): func.pecan = {}
        func.pecan['secured'] = True
        func.pecan['check_permissions'] = check_permissions
        return func
    return wrap


def walk_controller(root_class, controller):    
    if hasattr(controller, '_lookup'):
        # TODO: what about this?
        controller._check_security = root_class._perform_validation
    
    if not isinstance(controller, (int, dict)):
        for name, value in getmembers(controller):
            if name == 'controller': continue
            
            if ismethod(value):
                if iscontroller(value) and not value.pecan.get('unlocked', False):
                    value.pecan['secured'] = True
                    value.pecan['check_permissions'] = root_class.check_permissions
            elif hasattr(value, '__class__'):
                if name.startswith('__') and name.endswith('__'): continue
                walk_controller(root_class, value)
                

class SecureController(object):
    class __metaclass__(type):
        def __init__(cls, name, bases, dict_):
            walk_controller(cls, cls)
    
    @classmethod
    def check_permissions(cls):
        return True