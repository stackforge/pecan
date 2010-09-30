from pecan import Pecan, expose
from pecan.hooks import PecanHook, TransactionHook, HookController
from webtest import TestApp


class TestHooks(object):
    
    def test_basic_single_hook(self):
        run_hook = []
        
        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'
        
        class SimpleHook(PecanHook):
            def before(self, state):
                run_hook.append('before')

            def after(self, state):
                run_hook.append('after')

            def on_error(self, state, e):
                run_hook.append('error')
        
        app = TestApp(Pecan(RootController(), hooks=[SimpleHook()]))
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        
        assert len(run_hook) == 3
        assert run_hook[0] == 'before'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'after'
    
    def test_basic_multi_hook(self):
        run_hook = []
        
        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'
        
        class SimpleHook(PecanHook):
            def __init__(self, id):
                self.id = str(id)
            
            def before(self, state):
                run_hook.append('before'+self.id)

            def after(self, state):
                run_hook.append('after'+self.id)

            def on_error(self, state, e):
                run_hook.append('error'+self.id)
        
        app = TestApp(Pecan(RootController(), hooks=[
            SimpleHook(1), SimpleHook(2), SimpleHook(3)
        ]))
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        
        assert len(run_hook) == 7
        assert run_hook[0] == 'before1'
        assert run_hook[1] == 'before2'
        assert run_hook[2] == 'before3'
        assert run_hook[3] == 'inside'
        assert run_hook[4] == 'after1'
        assert run_hook[5] == 'after2'
        assert run_hook[6] == 'after3'
    
    def test_prioritized_hooks(self):
        run_hook = []
        
        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'
        
        class SimpleHook(PecanHook):
            def __init__(self, id):
                self.id = str(id)
            
            def before(self, state):
                run_hook.append('before'+self.id)

            def after(self, state):
                run_hook.append('after'+self.id)

            def on_error(self, state, e):
                run_hook.append('error'+self.id)
        
        papp = Pecan(RootController(), hooks=[
            SimpleHook(1), SimpleHook(2), SimpleHook(3)
        ])
        app = TestApp(papp)
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        
        assert len(run_hook) == 7
        assert run_hook[0] == 'before1'
        assert run_hook[1] == 'before2'
        assert run_hook[2] == 'before3'
        assert run_hook[3] == 'inside'
        assert run_hook[4] == 'after1'
        assert run_hook[5] == 'after2'
        assert run_hook[6] == 'after3'
        
        for i in range(len(run_hook)): run_hook.pop()
        
        papp.hooks[0].priority = 3
        papp.hooks[1].priority = 2
        papp.hooks[2].priority = 1
        
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        
        assert len(run_hook) == 7
        assert run_hook[0] == 'before3'
        assert run_hook[1] == 'before2'
        assert run_hook[2] == 'before1'
        assert run_hook[3] == 'inside'
        assert run_hook[4] == 'after3'
        assert run_hook[5] == 'after2'
        assert run_hook[6] == 'after1'
    
    def test_transaction_hook(self):
        run_hook = []
        
        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'
            
            @expose()
            def error(self):
                return [][1]
        
        class SimpleHook(PecanHook):
            def __init__(self, id):
                self.id = str(id)
            
            def before(self, state):
                run_hook.append('before'+self.id)

            def after(self, state):
                run_hook.append('after'+self.id)

            def on_error(self, state, e):
                run_hook.append('error'+self.id)
        
        def gen(event):
            return lambda: run_hook.append(event)
        
        app = TestApp(Pecan(RootController(), hooks=[
            TransactionHook(
                start    = gen('start'),
                start_ro = gen('start_ro'),
                commit   = gen('commit'),
                rollback = gen('rollback'),
                clear    = gen('clear')
            )
        ]))
        
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        
        assert len(run_hook) == 3
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'clear'
        
        for i in range(len(run_hook)): run_hook.pop()
        
        response = app.post('/')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        
        assert len(run_hook) == 4
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'commit'
        assert run_hook[3] == 'clear'
        
        for i in range(len(run_hook)): run_hook.pop()
        try:
            response = app.post('/error')
        except IndexError:
            pass
        
        assert len(run_hook) == 3
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'rollback'
        assert run_hook[2] == 'clear'
    
    def test_basic_isolated_hook(self):
        run_hook = []
        
        class SimpleHook(PecanHook):
            def before(self, state):
                run_hook.append('before')

            def after(self, state):
                run_hook.append('after')

            def on_error(self, state, e):
                run_hook.append('error')
        
        class SubController(HookController):
            __hooks__ = [SimpleHook()]
            
            @expose()
            def index(self):
                run_hook.append('inside_sub')
                return 'Inside here!'
        
        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'
            
            sub = SubController()
                
        app = TestApp(Pecan(RootController()))
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        
        assert len(run_hook) == 1
        assert run_hook[0] == 'inside'
        
        for i in range(len(run_hook)): run_hook.pop()
        
        response = app.get('/sub')
        assert response.status_int == 200
        assert response.body == 'Inside here!'
        
        assert len(run_hook) == 3
        assert run_hook[0] == 'before'
        assert run_hook[1] == 'inside_sub'
        assert run_hook[2] == 'after'
    
    def test_isolated_hook_with_global_hook(self):
        run_hook = []
        
        class SimpleHook(PecanHook):
            def __init__(self, id):
                self.id = str(id)
            
            def before(self, state):
                run_hook.append('before'+self.id)

            def after(self, state):
                run_hook.append('after'+self.id)

            def on_error(self, state, e):
                run_hook.append('error'+self.id)
        
        class SubController(HookController):
            __hooks__ = [SimpleHook(2)]
            
            @expose()
            def index(self):
                run_hook.append('inside_sub')
                return 'Inside here!'
        
        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'
            
            sub = SubController()
                
        app = TestApp(Pecan(RootController(), hooks=[SimpleHook(1)]))
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        
        assert len(run_hook) == 3
        assert run_hook[0] == 'before1'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'after1'
        
        for i in range(len(run_hook)): run_hook.pop()
        
        response = app.get('/sub')
        assert response.status_int == 200
        assert response.body == 'Inside here!'
        
        assert len(run_hook) == 5
        assert run_hook[0] == 'before2'
        assert run_hook[1] == 'before1'
        assert run_hook[2] == 'inside_sub'
        assert run_hook[3] == 'after2'
        assert run_hook[4] == 'after1'