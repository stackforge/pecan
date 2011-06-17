from inspect    import getmembers
from webob.exc  import HTTPFound

from util    import iscontroller, _cfg


__all__ = ['PecanHook', 'TransactionHook', 'HookController']


def walk_controller(root_class, controller, hooks):
    if not isinstance(controller, (int, dict)):
        for name, value in getmembers(controller):
            if name == 'controller': continue
            if name.startswith('__') and name.endswith('__'): continue
            
            if iscontroller(value):
                for hook in hooks:
                    value._pecan.setdefault('hooks', []).append(hook)
            elif hasattr(value, '__class__'):
                if name.startswith('__') and name.endswith('__'): continue
                walk_controller(root_class, value, hooks)


class HookController(object):
    '''
    A base class for controllers that would like to specify hooks on
    their controller methods. Simply create a list of hook objects 
    called ``__hooks__`` as a member of the controller's namespace.
    '''
    
    __hooks__ = []
    
    class __metaclass__(type):
        def __init__(cls, name, bases, dict_):
            walk_controller(cls, cls, dict_['__hooks__'])


class PecanHook(object):
    '''
    A base class for Pecan hooks. Inherit from this class to create your
    own hooks. Set a priority on a hook by setting the ``priority``
    attribute for the hook, which defaults to 100.
    '''
    
    priority = 100
    
    def on_route(self, state):
        '''
        Override this method to create a hook that gets called upon
        the start of routing.
        
        :param state: The Pecan ``state`` object for the current request.
        '''
        return
    
    def before(self, state):
        '''
        Override this method to create a hook that gets called after
        routing, but before the request gets passed to your controller.
        
        :param state: The Pecan ``state`` object for the current request.
        '''
        return
    
    def after(self, state):
        '''
        Override this method to create a hook that gets called after
        the request has been handled by the controller.
        
        :param state: The Pecan ``state`` object for the current request.
        '''
        return
    
    def on_error(self, state, e):
        '''
        Override this method to create a hook that gets called upon
        an exception being raised in your controller.
        
        :param state: The Pecan ``state`` object for the current request.
        :param e: The ``Exception`` object that was raised.
        '''
        return


class TransactionHook(PecanHook):
    '''
    A basic framework hook for supporting wrapping requests in
    transactions. By default, it will wrap all but ``GET`` and ``HEAD``
    requests in a transaction. Override the ``is_transactional`` method
    to define your own rules for what requests should be transactional.
    '''
    
    def __init__(self, start, start_ro, commit, rollback, clear):
        '''
        :param start: A callable that will bind to a writable database and start a transaction.
        :param start_ro: A callable that will bind to a readable database.
        :param commit: A callable that will commit the active transaction.
        :param rollback: A callable that will roll back the active transaction.
        :param clear: A callable that will clear your current context.
        '''
        
        self.start    = start
        self.start_ro = start_ro
        self.commit   = commit
        self.rollback = rollback
        self.clear    = clear

    def is_transactional(self, state):
        '''
        Decide if a request should be wrapped in a transaction, based
        upon the state of the request. By default, wraps all but ``GET``
        and ``HEAD`` requests in a transaction, along with respecting
        the ``transactional`` decorator from :mod:pecan.decorators.
        
        :param state: The Pecan state object for the current request.
        '''
        
        controller = getattr(state, 'controller', None)
        if controller:
            force_transactional = _cfg(controller).get('transactional', False)
        else:
            force_transactional = False

        if state.request.method not in ('GET', 'HEAD') or force_transactional:
            return True
        return False

    def on_route(self, state):
        state.request.error = False
        if self.is_transactional(state):
            state.request.transactional = True
            self.start()
        else:
            state.request.transactional = False
            self.start_ro()

    def before(self, state):
        if self.is_transactional(state) and not state.request.transactional:
            self.clear()
            state.request.transactional = True
            self.start()

    def on_error(self, state, e):
        #
        # If we should ignore redirects,
        # (e.g., shouldn't consider them rollback-worthy)
        # don't set `state.request.error = True`.
        #
        transactional_ignore_redirects = state.request.method not in ('GET', 'HEAD')
        if hasattr(state, 'controller'):
            transactional_ignore_redirects = _cfg(state.controller).get('transactional_ignore_redirects', transactional_ignore_redirects)
        if type(e) is HTTPFound and transactional_ignore_redirects is True:
            return
        state.request.error = True
    
    def after(self, state):
        if state.request.transactional:
            if state.request.error:
                self.rollback()
            else:
                self.commit()
                controller = getattr(state, 'controller', None)
                actions = _cfg(controller).get('after_commit', [])
                for action in actions:
                    action()
        self.clear()
