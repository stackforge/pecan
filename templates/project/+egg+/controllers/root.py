from pecan import expose, request
from formencode import Schema, validators as v


class SampleForm(Schema):
    name = v.String(not_empty=True)
    age = v.Int(not_empty=True)


class RootController(object):
    @expose('index.html')
    def index(self, name='', age=''):
        return dict(errors=request.validation_error, name=name, age=age)
    
    @expose('success.html', schema=SampleForm(), error_handler='index')
    def handle_form(self, name, age):
        return dict(name=name, age=age)
