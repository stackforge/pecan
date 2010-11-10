from pecan import make_app, expose, request, response, redirect
from webtest import TestApp

from formencode import validators, Schema


try:
    from json import dumps
except ImportError:
    from simplejson import dumps


class TestValidation(object):
    
    def test_simple_validation(self):
        class RegistrationSchema(Schema):
            first_name         = validators.String(not_empty=True)
            last_name          = validators.String(not_empty=True)
            email              = validators.Email()
            username           = validators.PlainText()
            password           = validators.String()
            password_confirm   = validators.String()
            age                = validators.Int()
            chained_validators = [
                validators.FieldsMatch('password', 'password_confirm')
            ]
        

        class RootController(object):
            @expose(schema=RegistrationSchema())
            def index(self, first_name, 
                            last_name, 
                            email, 
                            username, 
                            password,
                            password_confirm,
                            age):
                assert age == 31
                assert isinstance(age, int)
                return 'Success!'
            
            @expose(json_schema=RegistrationSchema())
            def json(self, data):
                assert data['age'] == 31
                assert isinstance(data['age'], int)
                return 'Success!'


        # test form submissions
        app = TestApp(make_app(RootController()))
        r = app.post('/', dict(
            first_name='Jonathan',
            last_name='LaCour',
            email='jonathan@cleverdevil.org',
            username='jlacour',
            password='123456',
            password_confirm='123456',
            age='31'
        ))
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test JSON submissions
        r = app.post('/json', dumps(dict(
            first_name='Jonathan',
            last_name='LaCour',
            email='jonathan@cleverdevil.org',
            username='jlacour',
            password='123456',
            password_confirm='123456',
            age='31'
        )), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'Success!'
        
    def test_simple_failure(self):
        class RegistrationSchema(Schema):
            first_name         = validators.String(not_empty=True)
            last_name          = validators.String(not_empty=True)
            email              = validators.Email()
            username           = validators.PlainText()
            password           = validators.String()
            password_confirm   = validators.String()
            age                = validators.Int()
            chained_validators = [
                validators.FieldsMatch('password', 'password_confirm')
            ]
        

        class SubSubRootController(object):
            @expose('json')
            def index(self):
                redirect('/sub/deeper/not_empty', internal=True)

            @expose('json')
            def not_empty(self, data):
                return data


        class SubRootController(object):
            @expose('json')
            def index(self):
                return '/sub'
                
            deeper = SubSubRootController()

        class RootController(object):

            sub = SubRootController()

            @expose()
            def errors(self, *args, **kwargs):
                assert request.validation_error is not None
                return 'There was an error!'
            
            @expose(schema=RegistrationSchema())
            def index(self, first_name, 
                            last_name, 
                            email, 
                            username, 
                            password,
                            password_confirm,
                            age):
                assert request.validation_error is not None
                return 'Success!'
            
            @expose(schema=RegistrationSchema(), error_handler='/errors')
            def with_handler(self, first_name, 
                            last_name, 
                            email, 
                            username, 
                            password,
                            password_confirm,
                            age):
                assert request.validation_error is not None
                return 'Success!'
            
            @expose(json_schema=RegistrationSchema())
            def json(self, data):
                assert request.validation_error is not None
                return 'Success!'
            
            @expose(json_schema=RegistrationSchema(), error_handler='/errors')
            def json_with_handler(self, data):
                assert request.validation_error is not None
                return 'Success!'
                
        # post some JSON to a sub controller and fail 
        app = TestApp(make_app(RootController()))
        resp = app.post('/sub/deeper', dumps({'name':'foobar'}))
        assert resp.body != {}



        # test without error handler
        app = TestApp(make_app(RootController()))
        r = app.post('/', dict(
            first_name='Jonathan',
            last_name='LaCour',
            email='jonathan@cleverdevil.org',
            username='jlacour',
            password='123456',
            password_confirm='654321',
            age='31'
        ))
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test with error handler
        app = TestApp(make_app(RootController()))
        r = app.post('/with_handler', dict(
            first_name='Jonathan',
            last_name='LaCour',
            email='jonathan@cleverdevil.org',
            username='jlacour',
            password='123456',
            password_confirm='654321',
            age='31'
        ))
        assert r.status_int == 200
        assert r.body == 'There was an error!'
        
        # test JSON without error handler
        r = app.post('/json', dumps(dict(
            first_name='Jonathan',
            last_name='LaCour',
            email='jonathan@cleverdevil.org',
            username='jlacour',
            password='123456',
            password_confirm='654321',
            age='31'
        )), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test JSON with error handler
        r = app.post('/json_with_handler', dumps(dict(
            first_name='Jonathan',
            last_name='LaCour',
            email='jonathan@cleverdevil.org',
            username='jlacour',
            password='123456',
            password_confirm='654321',
            age='31'
        )), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'There was an error!'
