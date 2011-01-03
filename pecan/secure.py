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
    """
    Used to apply security to a controller and its children.
    Implementations of SecureController should extend the
    `check_permissions` method to return a True or False
    value (depending on whether or not the user has access
    to the controller).
    """
    class __metaclass__(type):
        def __init__(cls, name, bases, dict_):
            walk_controller(cls, cls)
    
    @classmethod
    def check_permissions(cls):
        return True

        
class UnlockedControllerMeta(type):
    """
    Can be used to force (override) a controller and all of its
    subcontrollers to be unlocked/unsecured.
    
    This has the same effect as applying @pecan.secure.unlocked
    to every method in the class and its subclasses.
    """
    def __init__(cls, name, bases, ns):
        cls.walk_and_apply_unlocked(cls, cls)

    def walk_and_apply_unlocked(cls, root_class, controller):
        if not isinstance(controller, (int, dict)):
            for name, value in getmembers(controller):
                if name == 'controller': continue

                if ismethod(value):
                    if iscontroller(value):
                        value = unlocked(value)
                elif hasattr(value, '__class__'):
                    if name.startswith('__') and name.endswith('__'): continue
                    cls.walk_and_apply_unlocked(root_class, value)