from formencode import Schema, validators
from paste.recursive import ForwardRequestException
from unittest import TestCase
from webtest import TestApp

from pecan import Pecan, expose, request, response, redirect, abort
from pecan.templating import _builtin_renderers as builtin_renderers

import os


class TestBase(TestCase):
    
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
    
    def test_controller_args(self):
        class RootController(object):
            @expose()
            def index(self, id):
                return 'index: %s' % id
            
            @expose()
            def multiple(self, one, two):
                return 'multiple: %s, %s' % (one, two)
            
            @expose()
            def optional(self, id=None):
                return 'optional: %s' % str(id)
            
            @expose()
            def variable_args(self, *args):
                return 'variable_args: %s' % ', '.join(args)
            
            @expose()
            def variable_kwargs(self, **kwargs):
                data = ['%s=%s' % (key, kwargs[key]) for key in sorted(kwargs.keys())]
                return 'variable_kwargs: %s' % ', '.join(data)
            
            @expose()
            def variable_all(self, *args, **kwargs):
                data = ['%s=%s' % (key, kwargs[key]) for key in sorted(kwargs.keys())]
                return 'variable_all: %s' % ', '.join(list(args) + data)
            
            @expose()
            def eater(self, id, dummy=None, *args, **kwargs):
                data = ['%s=%s' % (key, kwargs[key]) for key in sorted(kwargs.keys())]
                return 'eater: %s, %s, %s' % (id, dummy, ', '.join(list(args) + data))
            
            @expose()
            def _route(self, args):
                if hasattr(self, args[0]):
                    return getattr(self, args[0]), args[1:]
                else:
                    return self.index, args
        
        app = TestApp(Pecan(RootController()))
        
        # required arg
        
        try:
            r = app.get('/')
            assert r.status_int != 200
        except Exception, ex:
            assert type(ex) == TypeError
            assert ex.args[0] == 'index() takes exactly 2 arguments (1 given)'
        
        r = app.get('/1')
        assert r.status_int == 200
        assert r.body == 'index: 1'
        
        r = app.get('/1/dummy', status=404)
        assert r.status_int == 404
        
        r = app.get('/?id=2')
        assert r.status_int == 200
        assert r.body == 'index: 2'
        
        r = app.get('/3?id=three')
        assert r.status_int == 200
        assert r.body == 'index: 3'
        
        r = app.post('/', {'id': '4'})
        assert r.status_int == 200
        assert r.body == 'index: 4'
        
        r = app.post('/4', {'id': 'four'})
        assert r.status_int == 200
        assert r.body == 'index: 4'
        
        r = app.get('/?id=5&dummy=dummy')
        assert r.status_int == 200
        assert r.body == 'index: 5'
        
        r = app.post('/', {'id': '6', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == 'index: 6'
        
        # multiple args
        
        r = app.get('/multiple/one/two')
        assert r.status_int == 200
        assert r.body == 'multiple: one, two'
        
        r = app.get('/multiple?one=three&two=four')
        assert r.status_int == 200
        assert r.body == 'multiple: three, four'
        
        r = app.post('/multiple', {'one': 'five', 'two': 'six'})
        assert r.status_int == 200
        assert r.body == 'multiple: five, six'
        
        # optional arg
        
        r = app.get('/optional')
        assert r.status_int == 200
        assert r.body == 'optional: None'
        
        r = app.get('/optional/1')
        assert r.status_int == 200
        assert r.body == 'optional: 1'
        
        r = app.get('/optional/2/dummy', status=404)
        assert r.status_int == 404
        
        r = app.get('/optional?id=2')
        assert r.status_int == 200
        assert r.body == 'optional: 2'
        
        r = app.get('/optional/3?id=three')
        assert r.status_int == 200
        assert r.body == 'optional: 3'
        
        r = app.post('/optional', {'id': '4'})
        assert r.status_int == 200
        assert r.body == 'optional: 4'
        
        r = app.post('/optional/5', {'id': 'five'})
        assert r.status_int == 200
        assert r.body == 'optional: 5'
        
        r = app.get('/optional?id=6&dummy=dummy')
        assert r.status_int == 200
        assert r.body == 'optional: 6'
        
        r = app.post('/optional', {'id': '7', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == 'optional: 7'
        
        # variable args
        
        r = app.get('/variable_args')
        assert r.status_int == 200
        assert r.body == 'variable_args: '
        
        r = app.get('/variable_args/1/dummy')
        assert r.status_int == 200
        assert r.body == 'variable_args: 1, dummy'
        
        r = app.get('/variable_args?id=2&dummy=dummy')
        assert r.status_int == 200
        assert r.body == 'variable_args: '
        
        r = app.post('/variable_args', {'id': '3', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == 'variable_args: '
        
        # variable keyword args
        
        r = app.get('/variable_kwargs')
        assert r.status_int == 200
        assert r.body == 'variable_kwargs: '
        
        r = app.get('/variable_kwargs/1/dummy', status=404)
        assert r.status_int == 404
        
        r = app.get('/variable_kwargs?id=2&dummy=dummy')
        assert r.status_int == 200
        assert r.body == 'variable_kwargs: dummy=dummy, id=2'
        
        r = app.post('/variable_kwargs', {'id': '3', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == 'variable_kwargs: dummy=dummy, id=3'
        
        # variable args & keyword args
        
        r = app.get('/variable_all')
        assert r.status_int == 200
        assert r.body == 'variable_all: '
        
        r = app.get('/variable_all/1')
        assert r.status_int == 200
        assert r.body == 'variable_all: 1'
        
        r = app.get('/variable_all/2/dummy')
        assert r.status_int == 200
        assert r.body == 'variable_all: 2, dummy'
        
        r = app.get('/variable_all/3?month=1&day=12')
        assert r.status_int == 200
        assert r.body == 'variable_all: 3, day=12, month=1'
        
        r = app.get('/variable_all/4?id=four&month=1&day=12')
        assert r.status_int == 200
        assert r.body == 'variable_all: 4, day=12, id=four, month=1'
        
        r = app.post('/variable_all/5/dummy')
        assert r.status_int == 200
        assert r.body == 'variable_all: 5, dummy'
        
        r = app.post('/variable_all/6', {'month': '1', 'day': '12'})
        assert r.status_int == 200
        assert r.body == 'variable_all: 6, day=12, month=1'
        
        r = app.post('/variable_all/7', {'id': 'seven', 'month': '1', 'day': '12'})
        assert r.status_int == 200
        assert r.body == 'variable_all: 7, day=12, id=seven, month=1'
        
        # the "everything" controller
        
        try:
            r = app.get('/eater')
            assert r.status_int != 200
        except Exception, ex:
            assert type(ex) == TypeError
            assert ex.args[0] == 'eater() takes at least 2 arguments (1 given)'
        
        r = app.get('/eater/1')
        assert r.status_int == 200
        assert r.body == 'eater: 1, None, '
        
        r = app.get('/eater/2/dummy')
        assert r.status_int == 200
        assert r.body == 'eater: 2, dummy, '
        
        r = app.get('/eater/3/dummy/foo/bar')
        assert r.status_int == 200
        assert r.body == 'eater: 3, dummy, foo, bar'
        
        r = app.get('/eater/4?month=1&day=12')
        assert r.status_int == 200
        assert r.body == 'eater: 4, None, day=12, month=1'
        
        r = app.get('/eater/5?id=five&month=1&day=12&dummy=dummy')
        assert r.status_int == 200
        assert r.body == 'eater: 5, dummy, day=12, month=1'
        
        r = app.post('/eater/6')
        assert r.status_int == 200
        assert r.body == 'eater: 6, None, '
        
        r = app.post('/eater/7/dummy')
        assert r.status_int == 200
        assert r.body == 'eater: 7, dummy, '
        
        r = app.post('/eater/8/dummy/foo/bar')
        assert r.status_int == 200
        assert r.body == 'eater: 8, dummy, foo, bar'
        
        r = app.post('/eater/9', {'month': '1', 'day': '12'})
        assert r.status_int == 200
        assert r.body == 'eater: 9, None, day=12, month=1'
        
        r = app.post('/eater/10', {'id': 'ten', 'month': '1', 'day': '12', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == 'eater: 10, dummy, day=12, month=1'
        
    def test_abort(self):
        class RootController(object):
            @expose()
            def index(self):
                abort(404)
        
        app = TestApp(Pecan(RootController()))
        r = app.get('/', status=404)
        assert r.status_int == 404
    
    def test_redirect(self):
        class RootController(object):
            @expose()
            def index(self):
                redirect('/testing')
            
            @expose()
            def internal(self):
                redirect('/testing', internal=True)
            
            @expose()
            def permanent(self):
                redirect('/testing', code=301)
            
            @expose()
            def testing(self):
                return 'it worked!'
        
        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 302
        r = r.follow()
        assert r.status_int == 200
        assert r.body == 'it worked!'
        
        self.assertRaises(ForwardRequestException, app.get, '/internal')
        
        r = app.get('/permanent')
        assert r.status_int == 301
        r = r.follow()
        assert r.status_int == 200
        assert r.body == 'it worked!'
    
    def test_streaming_response(self):
        import StringIO
        class RootController(object):
            @expose(content_type='text/plain')
            def test(self, foo):
                if foo == 'stream':
                    # mimic large file
                    contents = StringIO.StringIO('stream')
                    response.content_type='application/octet-stream'
                    contents.seek(0, os.SEEK_END)
                    response.content_length = contents.tell()
                    contents.seek(0, os.SEEK_SET)
                    response.app_iter = contents
                    return response
                else:
                    return 'plain text'

        app = TestApp(Pecan(RootController()))
        r = app.get('/test/stream')
        assert r.content_type == 'application/octet-stream'
        assert r.body == 'stream'

        r = app.get('/test/plain')
        assert r.content_type == 'text/plain'
        assert r.body == 'plain text'
    
    def test_request_state_cleanup(self):
        """
        After a request, the state local() should be totally clean
        except for state.app (so that objects don't leak between requests)
        """
        from pecan.core import state
        
        class RootController(object):
            @expose()
            def index(self):
                return '/'
        
        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        assert r.body == '/'
        
        assert state.__dict__.keys() == ['app']

    def test_extension(self):
        """
        Test extension splits
        """
        class RootController(object):
            @expose()
            def _default(self, *args):
                from pecan.core import request
                return request.context['extension']

        app = TestApp(Pecan(RootController()))
        r = app.get('/index.html')
        assert r.status_int == 200
        assert r.body == '.html'

        r = app.get('/image.png')
        assert r.status_int == 200
        assert r.body == '.png'

        r = app.get('/.vimrc')
        assert r.status_int == 200
        assert r.body == ''

        r = app.get('/gradient.js.js')
        assert r.status_int == 200
        assert r.body == '.js'




            

class TestEngines(object):
    
    template_path = os.path.join(os.path.dirname(__file__), 'templates')

    def test_genshi(self):
        if 'genshi' not in builtin_renderers:
            return

        class RootController(object):
            @expose('genshi:genshi.html')
            def index(self, name='Jonathan'):
                return dict(name=name)
        
        app = TestApp(Pecan(RootController(), template_path=self.template_path))    
        r = app.get('/')
        assert r.status_int == 200
        assert "<h1>Hello, Jonathan!</h1>" in r.body
        
        app = TestApp(Pecan(RootController(), template_path=self.template_path))
        r = app.get('/index.html?name=World')
        assert r.status_int == 200
        assert "<h1>Hello, World!</h1>" in r.body
    
    def test_kajiki(self):
        if 'kajiki' not in builtin_renderers:
            return

        class RootController(object):
            @expose('kajiki:kajiki.html')
            def index(self, name='Jonathan'):
                return dict(name=name)
        
        app = TestApp(Pecan(RootController(), template_path=self.template_path))
        r = app.get('/')
        assert r.status_int == 200
        assert "<h1>Hello, Jonathan!</h1>" in r.body
        
        app = TestApp(Pecan(RootController(), template_path=self.template_path))
        r = app.get('/index.html?name=World')
        assert r.status_int == 200
        assert "<h1>Hello, World!</h1>" in r.body
   
    def test_mako(self):
        if 'mako' not in builtin_renderers:
            return
        class RootController(object):
            @expose('mako:mako.html')
            def index(self, name='Jonathan'):
                return dict(name=name)
        
        app = TestApp(Pecan(RootController(), template_path=self.template_path))
        r = app.get('/')
        assert r.status_int == 200
        assert "<h1>Hello, Jonathan!</h1>" in r.body
        
        app = TestApp(Pecan(RootController(), template_path=self.template_path))
        r = app.get('/index.html?name=World')
        assert r.status_int == 200
        assert "<h1>Hello, World!</h1>" in r.body
    
    def test_json(self):
        from json import loads
        
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
