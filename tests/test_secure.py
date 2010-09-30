from pecan import expose, make_app
from pecan.secure import secure, unlocked, SecureController
from webob import exc
from webtest import TestApp, AppError
from py.test import raises

class TestSecure(object):
    
    def test_simple_secure(self):
        authorized = False
        
        class SecretController(SecureController):
            @expose()
            def index(self):
                return 'Index'
            
            @expose()
            @unlocked
            def allowed(self):
                return 'Allowed!'
            
            @classmethod
            def check_permissions(self):
                return authorized
        
        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'
            
            @expose()
            @secure(lambda: False)
            def locked(self):
                return 'No dice!'
            
            @expose()
            @secure(lambda: True)
            def unlocked(self):
                return 'Sure thing'
            
            secret = SecretController()
        
        
        app = TestApp(make_app(RootController(), static_root='tests/static'))
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        
        response = app.get('/unlocked')
        assert response.status_int == 200
        assert response.body == 'Sure thing'
        
        response = app.get('/locked', expect_errors=True)
        assert response.status_int == 401
        
        response = app.get('/secret', expect_errors=True)
        assert response.status_int == 401
        
        response = app.get('/secret/allowed')
        assert response.status_int == 200
        assert response.body == 'Allowed!'