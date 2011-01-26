from pecan import expose, request
from formencode import Schema, validators as v
from webob.exc import status_map


class SampleForm(Schema):
    name = v.String(not_empty=True)
    age = v.Int(not_empty=True)


class RootController(object):
    @expose('index.html')
    def index(self, name='', age=''):
        return dict(errors=request.validation_errors, name=name, age=age)
    
    @expose('success.html', schema=SampleForm(), error_handler='index')
    def handle_form(self, name, age):
        return dict(name=name, age=age)
    
    @expose('error.html')
    def error(self, status):
        try:
            status = int(status)
        except ValueError:
            status = 0
        message = getattr(status_map.get(status), 'explanation', '')
        return dict(status=status, message=message)
