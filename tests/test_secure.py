from unittest import TestCase

from pecan import expose, make_app
from pecan.secure import secure, unlocked, SecureController, Protected
from webtest import TestApp

try:
    set()
except:
    from sets import Set as set

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
        
    def test_unlocked_attribute(self):
        class AuthorizedSubController(object):
            @expose()
            def index(self):
                return 'Index'

            @expose()                
            def allowed(self):
                return 'Allowed!'

        class SecretController(SecureController):
            @expose()
            def index(self):
                return 'Index'

            @expose()
            @unlocked
            def allowed(self):
                return 'Allowed!'

            authorized = unlocked(AuthorizedSubController())

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
        
        response = app.get('/secret/authorized')
        assert response.status_int == 200
        assert response.body == 'Index'    
        
        response = app.get('/secret/authorized/allowed')
        assert response.status_int == 200
        assert response.body == 'Allowed!'

    def test_state_attribute(self):
        from pecan.secure import Any, Protected
        assert repr(Any) == '<SecureState Any>'
        assert bool(Any) is False

        assert repr(Protected) == '<SecureState Protected>'
        assert bool(Protected) is True

class TestObjectPathSecurity(TestCase):
    def setUp(self):
        permissions_checked = getattr(self, 'permissions_checked', set())
        class DeepSecretController(SecureController):
            authorized = False
            @expose()
            @unlocked
            def _lookup(self, someID, *remainder):
                if someID == 'notfound':
                    return None
                return SubController(someID), remainder
            
            @expose()
            def index(self):
                return 'Deep Secret'

            @classmethod
            def check_permissions(self):
                permissions_checked.add('deepsecret')
                return self.authorized

        deepsecret_instance = DeepSecretController()

        class SubController(object):
            def __init__(self, myID):
                self.myID = myID

            @expose()
            def index(self):
                return 'Index %s' % self.myID

            deepsecret = DeepSecretController()

        class SecretController(SecureController):
            authorized = False
            @expose()
            def _lookup(self, someID, *remainder):
                if someID == 'notfound':
                    return None
                return SubController(someID), remainder

            @classmethod
            def check_permissions(self):
                permissions_checked.add('secretcontroller')
                return self.authorized

        class NotSecretController(object):
            @expose()
            def _lookup(self, someID, *remainder):
                if someID == 'notfound':
                    return None
                return SubController(someID), remainder

        class RootController(object):
            secret = SecretController()
            notsecret = NotSecretController()

        self.deepsecret_cls = DeepSecretController
        self.secret_cls = SecretController

        self.permissions_checked = permissions_checked
        self.app = TestApp(make_app(RootController(), static_root='tests/static'))

    def tearDown(self):
        self.permissions_checked.clear()
        self.secret_cls.authorized = False
        self.deepsecret_cls.authorized = False

    def test_sub_of_both_not_secret(self):
        response = self.app.get('/notsecret/hi/')
        assert response.status_int == 200
        assert response.body == 'Index hi'

    def test_protected_lookup(self):
        response = self.app.get('/secret/hi/', expect_errors=True)
        assert response.status_int == 401

        self.secret_cls.authorized = True
        response = self.app.get('/secret/hi/')
        assert response.status_int == 200
        assert response.body == 'Index hi'
        assert 'secretcontroller' in self.permissions_checked

    def test_secured_notfound_lookup(self):
        response = self.app.get('/secret/notfound/', expect_errors=True)
        assert response.status_int == 404

    def test_secret_through_lookup(self):
        response = self.app.get('/notsecret/hi/deepsecret/', expect_errors=True)
        assert response.status_int == 401

    def test_layered_protection(self):
        response = self.app.get('/secret/hi/deepsecret/', expect_errors=True)
        assert response.status_int == 401
        assert 'secretcontroller' in self.permissions_checked

        self.secret_cls.authorized = True
        response = self.app.get('/secret/hi/deepsecret/', expect_errors=True)
        assert response.status_int == 401
        assert 'secretcontroller' in self.permissions_checked
        assert 'deepsecret' in self.permissions_checked

        self.deepsecret_cls.authorized = True
        response = self.app.get('/secret/hi/deepsecret/')
        assert response.status_int == 200
        assert response.body == 'Deep Secret'
        assert 'secretcontroller' in self.permissions_checked
        assert 'deepsecret' in self.permissions_checked

    def test_cyclical_protection(self):
        self.secret_cls.authorized = True
        self.deepsecret_cls.authorized = True
        response = self.app.get('/secret/1/deepsecret/2/deepsecret/')
        assert response.status_int == 200
        assert response.body == 'Deep Secret'
        assert 'secretcontroller' in self.permissions_checked
        assert 'deepsecret' in self.permissions_checked

    def test_unlocked_lookup(self):
        response = self.app.get('/notsecret/1/deepsecret/2/')
        assert response.status_int == 200
        assert response.body == 'Index 2'
        assert 'deepsecret' not in self.permissions_checked

        response = self.app.get('/notsecret/1/deepsecret/notfound/', expect_errors=True)
        assert response.status_int == 404
        assert 'deepsecret' not in self.permissions_checked

    def test_mixed_protection(self):
        self.secret_cls.authorized = True
        response = self.app.get('/secret/1/deepsecret/notfound/', expect_errors=True)
        assert response.status_int == 404
        assert 'secretcontroller' in self.permissions_checked
        assert 'deepsecret' not in self.permissions_checked

