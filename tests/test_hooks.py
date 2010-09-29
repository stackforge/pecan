from pecan import Pecan, expose
from pecan.hooks import PecanHook, TransactionHook
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
        