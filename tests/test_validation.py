from formencode import ForEach, Schema, validators
from webtest import TestApp

import os.path

from pecan import make_app, expose, request, response, redirect, ValidationException
from pecan.templating import _builtin_renderers as builtin_renderers

try:
    from simplejson import dumps
except ImportError:
    from json import dumps


class TestValidation(object):
    
    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    
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
                assert isinstance(last_name, unicode)
                assert isinstance(first_name, unicode)
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
        

        class RootController(object):

            @expose()
            def errors(self, *args, **kwargs):
                assert len(request.pecan['validation_errors']) > 0
                return 'There was an error!'
            
            @expose(schema=RegistrationSchema())
            def index(self, first_name, 
                            last_name, 
                            email, 
                            username, 
                            password,
                            password_confirm,
                            age):
                assert len(request.pecan['validation_errors']) > 0
                return 'Success!'
            
            @expose(schema=RegistrationSchema(), error_handler='/errors')
            def with_handler(self, first_name, 
                            last_name, 
                            email, 
                            username, 
                            password,
                            password_confirm,
                            age):
                assert len(request.pecan['validation_errors']) > 0
                return 'Success!'
            
            @expose(json_schema=RegistrationSchema())
            def json(self, data):
                assert len(request.pecan['validation_errors']) > 0
                return 'Success!'
            
            @expose(json_schema=RegistrationSchema(), error_handler='/errors')
            def json_with_handler(self, data):
                assert len(request.pecan['validation_errors']) > 0
                return 'Success!'
                

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

    def test_with_variable_decode(self):
        
        class ColorSchema(Schema):
            colors = ForEach(validators.String(not_empty=True))
        
        class RootController(object):
            
            @expose()
            def errors(self, *args, **kwargs):
                return 'Error with %s!' % ', '.join(request.pecan['validation_errors'].keys())
            
            @expose(schema=ColorSchema(), 
                    variable_decode=True)
            def index(self, **kwargs):
                if request.pecan['validation_errors']:
                    return ', '.join(request.pecan['validation_errors'].keys())
                else:
                    return 'Success!'
            
            @expose(schema=ColorSchema(), 
                    error_handler='/errors', 
                    variable_decode=True)
            def with_handler(self, **kwargs):
                if request.pecan['validation_errors']:
                    return ', '.join(request.pecan['validation_errors'].keys())
                else:
                    return 'Success!'
            
            @expose(json_schema=ColorSchema(), 
                    variable_decode=True)
            def json(self, data):
                if request.pecan['validation_errors']:
                    return ', '.join(request.pecan['validation_errors'].keys())
                else:
                    return 'Success!'
            
            @expose(json_schema=ColorSchema(), 
                    error_handler='/errors', 
                    variable_decode=True)
            def json_with_handler(self, data):
                if request.pecan['validation_errors']:
                    return ', '.join(request.pecan['validation_errors'].keys())
                else:
                    return 'Success!'
            
            @expose(schema=ColorSchema(),
                    variable_decode=dict())
            def custom(self, **kwargs):
                if request.pecan['validation_errors']:
                    return ', '.join(request.pecan['validation_errors'].keys())
                else:
                    return 'Success!'
            
            @expose(schema=ColorSchema(),
                    error_handler='/errors',
                    variable_decode=dict())
            def custom_with_handler(self, **kwargs):
                if request.pecan['validation_errors']:
                    return ', '.join(request.pecan['validation_errors'].keys())
                else:
                    return 'Success!'
            
            @expose(json_schema=ColorSchema(),
                    variable_decode=dict())
            def custom_json(self, data):
                if request.pecan['validation_errors']:
                    return ', '.join(request.pecan['validation_errors'].keys())
                else:
                    return 'Success!'

            @expose(json_schema=ColorSchema(),
                    error_handler='/errors',
                    variable_decode=dict())
            def custom_json_with_handler(self, data):
                if request.pecan['validation_errors']:
                    return ', '.join(request.pecan['validation_errors'].keys())
                else:
                    return 'Success!'

            @expose(schema=ColorSchema(),
                    variable_decode=dict(dict_char='-', list_char='.'))
            def alternate(self, **kwargs):
                if request.pecan['validation_errors']:
                    return ', '.join(request.pecan['validation_errors'].keys())
                else:
                    return 'Success!'
            
            @expose(schema=ColorSchema(),
                    error_handler='/errors',
                    variable_decode=dict(dict_char='-', list_char='.'))
            def alternate_with_handler(self, **kwargs):
                if request.pecan['validation_errors']:
                    return ', '.join(request.pecan['validation_errors'].keys())
                else:
                    return 'Success!'
            
            @expose(json_schema=ColorSchema(),
                    variable_decode=dict(dict_char='-', list_char='.'))
            def alternate_json(self, data):
                if request.pecan['validation_errors']:
                    return ', '.join(request.pecan['validation_errors'].keys())
                else:
                    return 'Success!'

            @expose(json_schema=ColorSchema(),
                    error_handler='/errors',
                    variable_decode=dict(dict_char='-', list_char='.'))
            def alternate_json_with_handler(self, data):
                if request.pecan['validation_errors']:
                    return ', '.join(request.pecan['validation_errors'].keys())
                else:
                    return 'Success!'
        
        # test without error handler
        app = TestApp(make_app(RootController()))
        r = app.post('/', {
            'colors-0' : 'blue',
            'colors-1' : 'red'
        })
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test failure without error handler
        r = app.post('/', {
            'colors-0' : 'blue',
            'colors-1' : ''
        })
        assert r.status_int == 200
        assert r.body == 'colors-1'
        
        # test with error handler
        r = app.post('/with_handler', {
            'colors-0' : 'blue',
            'colors-1' : 'red'
        })
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test failure with error handler
        r = app.post('/with_handler', {
            'colors-0' : '',
            'colors-1' : 'red'
        })
        assert r.status_int == 200
        assert r.body == 'Error with colors-0!'
        
        # test JSON without error handler
        r = app.post('/json', dumps({
            'colors-0' : 'blue',
            'colors-1' : 'red'
        }), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test JSON failure without error handler
        r = app.post('/json', dumps({
            'colors-0' : 'blue',
            'colors-1' : ''
        }), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'colors-1'
        
        # test JSON with error handler
        r = app.post('/json_with_handler', dumps({
            'colors-0' : 'blue',
            'colors-1' : 'red'
        }), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test JSON failure with error handler
        r = app.post('/json_with_handler', dumps({
            'colors-0' : '',
            'colors-1' : 'red'
        }), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'Error with colors-0!'
        
        # test custom without error handler
        r = app.post('/custom', {
            'colors-0' : 'blue',
            'colors-1' : 'red'
        })
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test custom failure without error handler
        r = app.post('/custom', {
            'colors-0' : 'blue',
            'colors-1' : ''
        })
        assert r.status_int == 200
        assert r.body == 'colors-1'
        
        # test custom with error handler
        r = app.post('/custom_with_handler', {
            'colors-0' : 'blue',
            'colors-1' : 'red'
        })
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test custom failure with error handler
        r = app.post('/custom_with_handler', {
            'colors-0' : '',
            'colors-1' : 'red'
        })
        assert r.status_int == 200
        assert r.body == 'Error with colors-0!'
        
        # test custom JSON without error handler
        r = app.post('/custom_json', dumps({
            'colors-0' : 'blue',
            'colors-1' : 'red'
        }), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test custom JSON failure without error handler
        r = app.post('/custom_json', dumps({
            'colors-0' : 'blue',
            'colors-1' : ''
        }), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'colors-1'
        
        # test custom JSON with error handler
        r = app.post('/custom_json_with_handler', dumps({
            'colors-0' : 'blue',
            'colors-1' : 'red'
        }), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test custom JSON failure with error handler
        r = app.post('/custom_json_with_handler', dumps({
            'colors-0' : '',
            'colors-1' : 'red'
        }), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'Error with colors-0!'
        
        # test alternate without error handler
        r = app.post('/alternate', {
            'colors.0' : 'blue',
            'colors.1' : 'red'
        })
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test alternate failure without error handler
        r = app.post('/alternate', {
            'colors.0' : 'blue',
            'colors.1' : ''
        })
        assert r.status_int == 200
        assert r.body == 'colors.1'
        
        # test alternate with error handler
        r = app.post('/alternate_with_handler', {
            'colors.0' : 'blue',
            'colors.1' : 'red'
        })
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test alternate failure with error handler
        r = app.post('/alternate_with_handler', {
            'colors.0' : '',
            'colors.1' : 'red'
        })
        assert r.status_int == 200
        assert r.body == 'Error with colors.0!'
        
        # test alternate JSON without error handler
        r = app.post('/alternate_json', dumps({
            'colors.0' : 'blue',
            'colors.1' : 'red'
        }), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test alternate JSON failure without error handler
        r = app.post('/alternate_json', dumps({
            'colors.0' : 'blue',
            'colors.1' : ''
        }), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'colors.1'
        
        # test alternate JSON with error handler
        r = app.post('/alternate_json_with_handler', dumps({
            'colors.0' : 'blue',
            'colors.1' : 'red'
        }), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test alternate JSON failure with error handler
        r = app.post('/alternate_json_with_handler', dumps({
            'colors.0' : '',
            'colors.1' : 'red'
        }), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'Error with colors.0!'
    
    def test_htmlfill(self):
        
        if 'mako' not in builtin_renderers:
            return
        
        class ColorSchema(Schema):
            colors = ForEach(validators.String(not_empty=True))
        
        class NameSchema(Schema):
            name = validators.String(not_empty=True)
        
        class RootController(object):
            
            @expose(template='mako:form_colors.html',
                    schema=ColorSchema(), 
                    variable_decode=True)
            def index(self, **kwargs):
                if request.pecan['validation_errors']:
                    return dict()
                else:
                    return dict(data=kwargs)
            
            @expose(schema=ColorSchema(),
                    error_handler='/errors_with_handler',
                    variable_decode=True)
            def with_handler(self, **kwargs):
                return ', '.join(kwargs['colors'])
            
            @expose('mako:form_colors.html')
            def errors_with_handler(self):
                return dict()
            
            @expose(template='mako:form_name.html',
                    schema=NameSchema(),
                    htmlfill=dict(auto_insert_errors=True))
            def with_errors(self, **kwargs):
                return kwargs
            
            @expose(schema=NameSchema(),
                    error_handler='/errors_with_handler_and_errors',
                    htmlfill=dict(auto_insert_errors=True))
            def with_handler_and_errors(self, **kwargs):
                return kwargs['name']
            
            @expose('mako:form_name.html')
            def errors_with_handler_and_errors(self):
                return dict()
            
            @expose(template='json',
                    schema=NameSchema(),
                    htmlfill=dict(auto_insert_errors=True))
            def json(self, **kwargs):
                if request.pecan['validation_errors']:
                    return dict(error_with=request.pecan['validation_errors'].keys())
                else:
                    return kwargs
        
        def _get_contents(filename):
            return open(os.path.join(self.template_path, filename), 'r').read()
        
        # test without error handler
        app = TestApp(make_app(RootController(), template_path=self.template_path))
        r = app.post('/', {
            'colors-0' : 'blue',
            'colors-1' : 'red'
        })
        assert r.status_int == 200
        assert r.body == _get_contents('form_colors_valid.html')
        
        # test failure without error handler
        r = app.post('/', {
            'colors-0' : 'blue',
            'colors-1' : ''
        })
        assert r.status_int == 200
        assert r.body == _get_contents('form_colors_invalid.html')
        
        # test with error handler
        r = app.post('/with_handler', {
            'colors-0' : 'blue',
            'colors-1' : 'red'
        })
        assert r.status_int == 200
        assert r.body == 'blue, red'
        
        # test failure with error handler
        r = app.post('/with_handler', {
            'colors-0' : 'blue',
            'colors-1' : ''
        })
        assert r.status_int == 200
        assert r.body == _get_contents('form_colors_invalid.html')
        
        # test with errors
        r = app.post('/with_errors', {
            'name' : 'Yoann'
        })
        assert r.status_int == 200
        assert r.body == _get_contents('form_name_valid.html')
        
        # test failure with errors
        r = app.post('/with_errors', {
            'name' : ''
        })
        assert r.status_int == 200
        assert r.body == _get_contents('form_name_invalid.html')
        
        # test with error handler and errors
        r = app.post('/with_handler_and_errors', {
            'name' : 'Yoann'
        })
        assert r.status_int == 200
        assert r.body == 'Yoann'
        
        # test failure with error handler and errors
        r = app.post('/with_handler_and_errors', {
            'name' : ''
        })
        assert r.status_int == 200
        assert r.body == _get_contents('form_name_invalid.html')
        
        # test JSON
        r = app.post('/json', {
            'name' : 'Yoann'
        })
        assert r.status_int == 200
        assert r.body == dumps(dict(name='Yoann'))
        
        # test JSON failure
        r = app.post('/json', {
            'name' : ''
        })
        assert r.status_int == 200
        assert r.body == dumps(dict(error_with=['name']))
                
    def test_htmlfill_static(self):

        if 'mako' not in builtin_renderers:
            return

        class LoginSchema(Schema):
            username = validators.String(not_empty=True)
            password = validators.String(not_empty=True)            

        class RootController(object):

            @expose(template='mako:form_login.html',
                    schema=LoginSchema())
            def index(self, **kwargs):
                if request.pecan['validation_errors']:
                    return dict()
                else:
                    return dict(data=kwargs)

            @expose(schema=LoginSchema(),
                    error_handler='/errors_with_handler')
            def with_handler(self, **kwargs):
                return '%s:%s' % (kwargs['username'], kwargs['password'])

            @expose('mako:form_login.html')
            def errors_with_handler(self):
                return dict()             

        def _get_contents(filename):
            return open(os.path.join(self.template_path, filename), 'r').read()

        # test without error handler
        app = TestApp(make_app(RootController(), template_path=self.template_path))
        r = app.post('/', {
            'username' : 'ryan',
            'password' : 'password'
        })
        assert r.status_int == 200
        assert r.body == _get_contents('form_login_valid.html')

        # test failure without error handler
        r = app.post('/', {
            'username' : 'ryan',
            'password' : ''
        })
        assert r.status_int == 200
        assert r.body == _get_contents('form_login_invalid.html')

        # test with error handler
        r = app.post('/with_handler', {
            'username' : 'ryan',
            'password' : 'password'
        })
        assert r.status_int == 200
        assert r.body == 'ryan:password'

        # test failure with error handler
        r = app.post('/with_handler', {
            'username' : 'ryan',
            'password' : ''
        })
        assert r.status_int == 200
        assert r.body == _get_contents('form_login_invalid.html')
    
    def test_error_for(self):
        
        if 'mako' not in builtin_renderers:
            return
        
        class ColorSchema(Schema):
            colors = ForEach(validators.String(not_empty=True))
        
        class RootController(object):
            
            @expose(template='mako:error_for.html')
            def errors(self, *args, **kwargs):
                return dict()
            
            @expose(template='mako:error_for.html',
                    schema=ColorSchema(), 
                    variable_decode=True)
            def index(self, **kwargs):
                return dict()
            
            @expose(schema=ColorSchema(), 
                    error_handler='/errors', 
                    variable_decode=True)
            def with_handler(self, **kwargs):
                return dict()
            
            @expose(template='mako:error_for.html',
                    json_schema=ColorSchema(), 
                    variable_decode=True)
            def json(self, data):
                return dict()
            
            @expose(json_schema=ColorSchema(), 
                    error_handler='/errors', 
                    variable_decode=True)
            def json_with_handler(self, data):
                return dict()
        
        # test without error handler
        app = TestApp(make_app(RootController(), template_path=self.template_path))
        r = app.post('/', {
            'colors-0' : 'blue',
            'colors-1' : 'red'
        })
        assert r.status_int == 200
        assert r.body == ''
        
        # test failure without error handler
        r = app.post('/', {
            'colors-0' : 'blue',
            'colors-1' : ''
        })
        assert r.status_int == 200
        assert r.body == 'Please enter a value'
        
        # test failure with error handler
        r = app.post('/with_handler', {
            'colors-0' : 'blue',
            'colors-1' : ''
        })
        assert r.status_int == 200
        assert r.body == 'Please enter a value'
        
        # test JSON failure without error handler
        r = app.post('/json', dumps({
            'colors-0' : 'blue',
            'colors-1' : ''
        }), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'Please enter a value'
        
        # test JSON failure with error handler
        r = app.post('/json_with_handler', dumps({
            'colors-0' : 'blue',
            'colors-1' : ''
        }), [('content-type', 'application/json')])
        assert r.status_int == 200
        assert r.body == 'Please enter a value'
    
    def test_callable_error_handler(self):
        
        class ColorSchema(Schema):
            colors = ForEach(validators.String(not_empty=True))
        
        class RootController(object):
            
            @expose()
            def errors(self, *args, **kwargs):
                return 'There was an error!'
            
            @expose(schema=ColorSchema(), 
                    error_handler=lambda: '/errors',
                    variable_decode=True)
            def index(self, **kwargs):
                return 'Success!'
        
        # test with error handler
        app = TestApp(make_app(RootController()))
        r = app.post('/', {
            'colors-0' : 'blue',
            'colors-1' : 'red'
        })
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test with error handler
        r = app.post('/', {
            'colors-0' : 'blue',
            'colors-1' : ''
        })
        assert r.status_int == 200
        assert r.body == 'There was an error!'
    
    def test_validation_exception(self):
        
        if 'mako' not in builtin_renderers:
            return
        
        class NameSchema(Schema):
            name = validators.String(not_empty=True)
        
        class SubController(object):
            @expose()
            def _route(self, *args):
                raise ValidationException('/success')
        
        class RootController(object):
            
            sub = SubController()
            
            @expose('mako:form_name.html')
            def errors_name(self):
                return dict()
            
            @expose(schema=NameSchema(), 
                    error_handler='/errors_name',
                    htmlfill=dict(auto_insert_errors=True))
            def name(self, name):
                raise ValidationException(errors={'name': 'Names must be unique'})
            
            @expose()
            def success(self):
                return 'Success!'
        
        def _get_contents(filename):
            return open(os.path.join(self.template_path, filename), 'r').read()
        
        # test exception with no controller
        app = TestApp(make_app(RootController(), template_path=self.template_path))
        r = app.get('/sub')
        assert r.status_int == 200
        assert r.body == 'Success!'
        
        # test exception with additional errors
        r = app.post('/name', {'name': 'Yoann'})
        assert r.status_int == 200
        assert r.body == _get_contents('form_name_invalid_custom.html')
