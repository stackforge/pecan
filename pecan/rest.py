from decorators import expose
from pecan import request


class RestController(object):
    # TODO: implement the following:
    #   - get, new, edit, post_delete, get_delete
    #   - see: http://turbogears.org/2.1/docs/modules/tgcontroller.html
    
    @expose()
    def _route(self, args):
        method = request.GET.get('_method', request.method)
        
        if method == 'GET':
            if len(args):
                return self.get_one, args
            return self.get_all, []
        elif method == 'POST':
            return self.post, []
        elif method == 'PUT' and len(args):
            return self.put, args
        elif method == 'DELETE' and len(args):
            return self.delete, args
    
    @expose()
    def get_one(self, id):
        raise NotImplemented
    
    @expose()
    def get_all(self):
        raise NotImplemented
    
    @expose()
    def post(self):
        raise NotImplemented
    
    @expose()
    def put(self, id):
        raise NotImplemented
    
    @expose()
    def delete(self, id):
        raise NotImplemented