import os
from pecan import expose, make_app
from webtest import TestApp

class TestStatic(object):
    
    def test_simple_static(self):    
        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'
        
        # make sure Cascade is working properly
        text = os.path.join(os.path.dirname(__file__), 'static/text.txt')
        static_root = os.path.join(os.path.dirname(__file__), 'static')

        app = TestApp(make_app(RootController(), static_root=static_root))
        response = app.get('/index.html')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        
        # get a static resource
        response = app.get('/text.txt')
        assert response.status_int == 200
        assert response.body == open(text, 'rb').read()
