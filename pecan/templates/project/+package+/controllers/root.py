from pecan import expose
from formencode import Schema, validators as v
from webob.exc import status_map


class SampleForm(Schema):
    name = v.String(not_empty=True)
    age = v.Int(not_empty=True)


class RootController(object):

    @expose(
        generic     = True, 
        template    = 'index.html'
    )
    def index(self):
        return dict()
    
    @index.when(
        method          = 'POST',
        template        = 'success.html',
        schema          = SampleForm(),
        error_handler   = '/index',
        htmlfill        = dict(auto_insert_errors = True, prefix_error = False)
    )
    def index_post(self, name, age):
        return dict(name=name)
    
    @expose('error.html')
    def error(self, status):
        try:
            status = int(status)
        except ValueError:
            status = 0
        message = getattr(status_map.get(status), 'explanation', '')
        return dict(status=status, message=message)
