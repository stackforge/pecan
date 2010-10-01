from pecan import expose

class RootController(object):
    @expose('kajiki:index.html')
    def index(self, name='World'):
        return dict(name=name)