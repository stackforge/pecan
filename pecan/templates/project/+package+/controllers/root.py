from pecan import expose, redirect
from formencode import Schema, validators as v
from webob.exc import status_map


class SearchForm(Schema):
    q = v.String(not_empty=True)


class RootController(object):

    @expose(
        generic     = True, 
        template    = 'index.html'
    )
    def index(self):
        return dict()
    
    @index.when(
        method          = 'POST',
        schema          = SearchForm(),
        error_handler   = '/index',
        htmlfill        = dict(auto_insert_errors = True)
    )
    def index_post(self, q):
        redirect('http://pecan.readthedocs.org/en/latest/search.html?q=%s' % q)
    
    @expose('error.html')
    def error(self, status):
        try:
            status = int(status)
        except ValueError: # pragma: no cover
            status = 500
        message = getattr(status_map.get(status), 'explanation', '')
        return dict(status=status, message=message)
