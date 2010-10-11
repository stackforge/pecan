from pecan import expose, make_app
from webtest import TestApp

class TestStatic(object):
    
    def test_simple_static(self):    
        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'
        
        # make sure Cascade is working properly
        app = TestApp(make_app(RootController(), static_root='tests/static'))
        response = app.get('/index.html')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        
        # get a static resource
        response = app.get('/text.txt')
        assert response.status_int == 200
        assert response.body == open('tests/static/text.txt', 'rb').read()