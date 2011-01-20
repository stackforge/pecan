from webob.exc  import HTTPFound
from util    import iscontroller


__all__ = ['PecanHook', 'TransactionHook', 'HookController']


def walk_controller(root_class, controller, hooks):
    if hasattr(controller, '_lookup'):
        # TODO: what about this?
        pass
        
    if not isinstance(controller, (int, dict)):
        for name, value in controller.__dict__.iteritems():
            if name == 'controller': continue
            if name.startswith('__') and name.endswith('__'): continue
            
            if iscontroller(value):
                for hook in hooks:
                    value._pecan.setdefault('hooks', []).append(hook)
            elif hasattr(value, '__class__'):
                if name.startswith('__') and name.endswith('__'): continue
                walk_controller(root_class, value, hooks)


class HookController(object):
    __hooks__ = []
    
    class __metaclass__(type):
        def __init__(cls, name, bases, dict_):
            walk_controller(cls, cls, dict_['__hooks__'])


class PecanHook(object):
    priority = 100
    
    def on_route(self ,state):
        return
    
    def before(self, state):
        return
    
    def after(self, state):
        return
    
    def on_error(self, state, e):
        return


class TransactionHook(PecanHook):
    def __init__(self, start, start_ro, commit, rollback, clear):
        self.start    = start
        self.start_ro = start_ro
        self.commit   = commit
        self.rollback = rollback
        self.clear    = clear

    def is_transactional(self, state):
        controller = getattr(state, 'controller', None)
        if controller:
            force_transactional = getattr(state.controller, '__transactional__', False)
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
        transactional_ignore_redirects = getattr(
            getattr(state, 'controller', None), 
            '__transactional_ignore_redirects__',
            state.request.method not in ('GET', 'HEAD')
        )
        if type(e) is HTTPFound and transactional_ignore_redirects is True:
            return
        state.request.error = True
    
    def after(self, state):
        if state.request.transactional:
            if state.request.error:
                self.rollback()
            else:
                self.commit()
        self.clear()
