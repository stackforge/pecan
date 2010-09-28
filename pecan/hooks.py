class PecanHook(object):
    def before(self, state):
        pass
    
    def after(self, state):
        pass
    
    def on_error(self, state):
        pass


class TransactionHook(PecanHook):
    def __init__(self, start, start_ro, commit, rollback, clear):
        self.start    = start
        self.start_ro = start_ro
        self.commit   = commit
        self.rollback = rollback
        self.clear    = clear
    
    def is_transactional(self, state):
        if state.request.method not in ('GET', 'HEAD'):
            return True
        return False
    
    def before(self, state):
        state.request.error = False
        if self.is_transactional(state):
            state.request.transactional = True
            self.start()
        else:
            state.request.transactional = False
            self.start_ro()
    
    def on_error(self, state):
        state.request.error = True
        self.rollback()
    
    def after(self, state):
        if state.request.transactional:
            if state.request.error:
                self.rollback()
            else:
                self.commit()
        self.clear()