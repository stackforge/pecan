from pecan import Pecan, expose, request, response, redirect
from webtest import TestApp
from formencode import Schema, validators


class TestBase(object):
    
    def test_simple_app(self):    
        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'
        
        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        assert r.body == 'Hello, World!'
        
        r = app.get('/index')
        assert r.status_int == 200
        assert r.body == 'Hello, World!'
        
        r = app.get('/index.html')
        assert r.status_int == 200
        assert r.body == 'Hello, World!'
    
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
            r = app.get(path)
            assert r.status_int == 200
            assert r.body == path
    
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
        r = app.get('/')
        assert r.status_int == 200
        assert r.body == '/'
        
        r = app.get('/100')
        assert r.status_int == 200
        assert r.body == '/100'
        
        r = app.get('/100/name')
        assert r.status_int == 200
        assert r.body == '/100/name'
            

class TestEngines(object):
    
    def test_genshi(self):
        class RootController(object):
            @expose('genshi:genshi.html')
            def index(self, name='Jonathan'):
                return dict(name=name)
        
        app = TestApp(Pecan(RootController(), template_path='tests/templates'))
        r = app.get('/')
        assert r.status_int == 200
        assert "<h1>Hello, Jonathan!</h1>" in r.body
        
        app = TestApp(Pecan(RootController(), template_path='tests/templates'))
        r = app.get('/index.html?name=World')
        assert r.status_int == 200
        assert "<h1>Hello, World!</h1>" in r.body
    
    def test_kajiki(self):
        class RootController(object):
            @expose('kajiki:kajiki.html')
            def index(self, name='Jonathan'):
                return dict(name=name)
        
        app = TestApp(Pecan(RootController(), template_path='tests/templates'))
        r = app.get('/')
        assert r.status_int == 200
        assert "<h1>Hello, Jonathan!</h1>" in r.body
        
        app = TestApp(Pecan(RootController(), template_path='tests/templates'))
        r = app.get('/index.html?name=World')
        assert r.status_int == 200
        assert "<h1>Hello, World!</h1>" in r.body
    
    def test_mako(self):
        class RootController(object):
            @expose('mako:mako.html')
            def index(self, name='Jonathan'):
                return dict(name=name)
        
        app = TestApp(Pecan(RootController(), template_path='tests/templates'))
        r = app.get('/')
        assert r.status_int == 200
        assert "<h1>Hello, Jonathan!</h1>" in r.body
        
        app = TestApp(Pecan(RootController(), template_path='tests/templates'))
        r = app.get('/index.html?name=World')
        assert r.status_int == 200
        assert "<h1>Hello, World!</h1>" in r.body
    
    def test_json(self):
        from simplejson import loads
        
        expected_result = dict(name='Jonathan', age=30, nested=dict(works=True))
        
        class RootController(object):
            @expose('json')
            def index(self):
                return expected_result
        
        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        result = dict(loads(r.body))
        assert result == expected_result
    
    def test_controller_parameters(self):
        class RootController(object):
            @expose('json')
            def index(self, argument=None):
                assert argument == 'value'
                return dict()
        
        # arguments should get passed appropriately
        app = TestApp(Pecan(RootController()))
        r = app.get('/?argument=value')
        assert r.status_int == 200
        
        # extra arguments get stripped off
        r = app.get('/?argument=value&extra=not')
        assert r.status_int == 200
    
    def test_redirect(self):
        class RootController(object):
            @expose()
            def index(self):
                redirect('/testing')
            
            @expose()
            def testing(self):
                return 'it worked!'
        
        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 302
        r = r.follow()
        assert r.status_int == 200
        assert r.body == 'it worked!'
    
    def test_uri_to_parameter_mapping(self):
        class RootController(object):
            @expose()
            def test(self, one, two):
                assert one == '1'
                assert two == '2'
                return 'it worked'
                
        app = TestApp(Pecan(RootController()))
        r = app.get('/test/1/2')
        assert r.status_int == 200
        assert r.body == 'it worked'
    
    def test_uri_to_parameter_mapping_with_validation(self):
        class TestSchema(Schema):
            one = validators.Int(not_empty=True)
            two = validators.Int(not_empty=True)
        
        class RootController(object):
            @expose(schema=TestSchema())
            def test(self, one, two):
                assert request.validation_error is None
                assert one == 1
                assert two == 2
                return 'it worked'
            
            @expose(schema=TestSchema())
            def fail(self, one, two):
                assert request.validation_error is not None
                assert one == 'one'
                assert two == 'two'
                return 'it failed'
                
        app = TestApp(Pecan(RootController()))
        r = app.get('/test/1/2')
        assert r.status_int == 200
        assert r.body == 'it worked'
        
        r = app.get('/fail/one/two')
        assert r.status_int == 200
        assert r.body == 'it failed'
    
    def test_uri_to_parameter_mapping_with_varargs(self):
        class RootController(object):
            @expose()
            def test(self, *args):
                assert len(args) == 4
                assert args[0] == '1'
                assert args[1] == '2'
                assert args[2] == '3'
                assert args[3] == '4'
                return 'it worked'
        
        app = TestApp(Pecan(RootController()))
        r = app.get('/test/1/2/3/4')
        assert r.status_int == 200
        assert r.body == 'it worked'