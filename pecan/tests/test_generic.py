from pecan import Pecan, expose
from unittest import TestCase
from webtest import TestApp
try:
    from simplejson import dumps
except:
    from json import dumps  # noqa


class TestGeneric(TestCase):

    def test_simple_generic(self):
        class RootController(object):
            @expose(generic=True)
            def index(self):
                pass

            @index.when(method='POST', template='json')
            def do_post(self):
                return dict(result='POST')

            @index.when(method='GET')
            def do_get(self):
                return 'GET'

        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        assert r.body == 'GET'

        r = app.post('/')
        assert r.status_int == 200
        assert r.body == dumps(dict(result='POST'))

        r = app.get('/do_get', status=404)
        assert r.status_int == 404
