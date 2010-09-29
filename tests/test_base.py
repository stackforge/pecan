from pecan import Pecan, expose
from webtest import TestApp

class TestBase(object):
    
    def test_simple_app(self):    
        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'
        
        app = TestApp(Pecan(RootController()))
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        
        response = app.get('/index')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        
        response = app.get('/index.html')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
    
    def test_object_dispatch(self):
        class SubSubController(object):
            @expose()
            def index(self):
                return '/sub/sub'
            
            @expose()
            def deeper(self):
                return '/sub/sub/deeper'
        
        class SubController(object):
            @expose()
            def index(self):
                return '/sub'
                
            @expose()
            def deeper(self):
                return '/sub/deeper'
                
            sub = SubSubController()
        
        class RootController(object):
            @expose()
            def index(self):
                return '/'
            
            @expose()
            def deeper(self):
                return '/deeper'
            
            sub = SubController()
        
        app = TestApp(Pecan(RootController()))
        for path in ('/', '/deeper', '/sub', '/sub/deeper', '/sub/sub', '/sub/sub/deeper'):
            response = app.get(path)
            assert response.status_int == 200
            assert response.body == path
    
    def test_lookup(self):
        class LookupController(object):
            def __init__(self, someID):
                self.someID = someID
            
            @expose()
            def index(self):
                return '/%s' % self.someID
            
            @expose()
            def name(self):
                return '/%s/name' % self.someID
        
        class RootController(object):
            @expose()
            def index(self):
                return '/'
            
            @expose()
            def _lookup(self, someID, *remainder):
                return LookupController(someID), remainder
        
        app = TestApp(Pecan(RootController()))
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == '/'
        
        response = app.get('/100')
        assert response.status_int == 200
        assert response.body == '/100'
        
        response = app.get('/100/name')
        assert response.status_int == 200
        assert response.body == '/100/name'
            

class TestEngines(object):
    
    def test_genshi(self):
        class RootController(object):
            @expose('genshi:genshi.html')
            def index(self, name='Jonathan'):
                return dict(name=name)
        
        app = TestApp(Pecan(RootController(), template_path='tests/templates'))
        response = app.get('/')
        assert response.status_int == 200
        assert "<h1>Hello, Jonathan!</h1>" in response.body
        
        app = TestApp(Pecan(RootController(), template_path='tests/templates'))
        response = app.get('/index.html?name=World')
        assert response.status_int == 200
        assert "<h1>Hello, World!</h1>" in response.body
    
    def test_kajiki(self):
        class RootController(object):
            @expose('kajiki:kajiki.html')
            def index(self, name='Jonathan'):
                return dict(name=name)
        
        app = TestApp(Pecan(RootController(), template_path='tests/templates'))
        response = app.get('/')
        assert response.status_int == 200
        assert "<h1>Hello, Jonathan!</h1>" in response.body
        
        app = TestApp(Pecan(RootController(), template_path='tests/templates'))
        response = app.get('/index.html?name=World')
        assert response.status_int == 200
        assert "<h1>Hello, World!</h1>" in response.body
    
    def test_mako(self):
        class RootController(object):
            @expose('mako:mako.html')
            def index(self, name='Jonathan'):
                return dict(name=name)
        
        app = TestApp(Pecan(RootController(), template_path='tests/templates'))
        response = app.get('/')
        assert response.status_int == 200
        assert "<h1>Hello, Jonathan!</h1>" in response.body
        
        app = TestApp(Pecan(RootController(), template_path='tests/templates'))
        response = app.get('/index.html?name=World')
        assert response.status_int == 200
        assert "<h1>Hello, World!</h1>" in response.body
    
    def test_json(self):
        from simplejson import loads
        
        expected_result = dict(name='Jonathan', age=30, nested=dict(works=True))
        
        class RootController(object):
            @expose('json')
            def index(self):
                return expected_result
        
        app = TestApp(Pecan(RootController()))
        response = app.get('/')
        assert response.status_int == 200
        result = dict(loads(response.body))
        assert result == expected_result