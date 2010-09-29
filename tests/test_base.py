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
        
        app = TestApp(Pecan(RootController()))
        response = app.get('/index')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        
        app = TestApp(Pecan(RootController()))
        response = app.get('/index.html')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
    
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