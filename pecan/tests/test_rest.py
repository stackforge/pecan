import struct
import warnings
try:
    from simplejson import dumps, loads
except:
    from json import dumps, loads  # noqa

from six import b as b_, PY3
from webtest import TestApp

from pecan import abort, expose, make_app, response, redirect
from pecan.rest import RestController
from pecan.tests import PecanTestCase


class TestRestController(PecanTestCase):

    def test_basic_rest(self):

        class OthersController(object):

            @expose()
            def index(self):
                return 'OTHERS'

            @expose()
            def echo(self, value):
                return str(value)

        class ThingsController(RestController):
            data = ['zero', 'one', 'two', 'three']

            _custom_actions = {'count': ['GET'], 'length': ['GET', 'POST']}

            others = OthersController()

            @expose()
            def get_one(self, id):
                return self.data[int(id)]

            @expose('json')
            def get_all(self):
                return dict(items=self.data)

            @expose()
            def length(self, id, value=None):
                length = len(self.data[int(id)])
                if value:
                    length += len(value)
                return str(length)

            @expose()
            def get_count(self):
                return str(len(self.data))

            @expose()
            def new(self):
                return 'NEW'

            @expose()
            def post(self, value):
                self.data.append(value)
                response.status = 302
                return 'CREATED'

            @expose()
            def edit(self, id):
                return 'EDIT %s' % self.data[int(id)]

            @expose()
            def put(self, id, value):
                self.data[int(id)] = value
                return 'UPDATED'

            @expose()
            def get_delete(self, id):
                return 'DELETE %s' % self.data[int(id)]

            @expose()
            def delete(self, id):
                del self.data[int(id)]
                return 'DELETED'

            @expose()
            def reset(self):
                return 'RESET'

            @expose()
            def post_options(self):
                return 'OPTIONS'

            @expose()
            def options(self):
                abort(500)

            @expose()
            def other(self):
                abort(500)

        class RootController(object):
            things = ThingsController()

        # create the app
        app = TestApp(make_app(RootController()))

        # test get_all
        r = app.get('/things')
        assert r.status_int == 200
        assert r.body == b_(dumps(dict(items=ThingsController.data)))

        # test get_one
        for i, value in enumerate(ThingsController.data):
            r = app.get('/things/%d' % i)
            assert r.status_int == 200
            assert r.body == b_(value)

        # test post
        r = app.post('/things', {'value': 'four'})
        assert r.status_int == 302
        assert r.body == b_('CREATED')

        # make sure it works
        r = app.get('/things/4')
        assert r.status_int == 200
        assert r.body == b_('four')

        # test edit
        r = app.get('/things/3/edit')
        assert r.status_int == 200
        assert r.body == b_('EDIT three')

        # test put
        r = app.put('/things/4', {'value': 'FOUR'})
        assert r.status_int == 200
        assert r.body == b_('UPDATED')

        # make sure it works
        r = app.get('/things/4')
        assert r.status_int == 200
        assert r.body == b_('FOUR')

        # test put with _method parameter and GET
        r = app.get('/things/4?_method=put', {'value': 'FOUR!'}, status=405)
        assert r.status_int == 405

        # make sure it works
        r = app.get('/things/4')
        assert r.status_int == 200
        assert r.body == b_('FOUR')

        # test put with _method parameter and POST
        r = app.post('/things/4?_method=put', {'value': 'FOUR!'})
        assert r.status_int == 200
        assert r.body == b_('UPDATED')

        # make sure it works
        r = app.get('/things/4')
        assert r.status_int == 200
        assert r.body == b_('FOUR!')

        # test get delete
        r = app.get('/things/4/delete')
        assert r.status_int == 200
        assert r.body == b_('DELETE FOUR!')

        # test delete
        r = app.delete('/things/4')
        assert r.status_int == 200
        assert r.body == b_('DELETED')

        # make sure it works
        r = app.get('/things')
        assert r.status_int == 200
        assert len(loads(r.body.decode())['items']) == 4

        # test delete with _method parameter and GET
        r = app.get('/things/3?_method=DELETE', status=405)
        assert r.status_int == 405

        # make sure it works
        r = app.get('/things')
        assert r.status_int == 200
        assert len(loads(r.body.decode())['items']) == 4

        # test delete with _method parameter and POST
        r = app.post('/things/3?_method=DELETE')
        assert r.status_int == 200
        assert r.body == b_('DELETED')

        # make sure it works
        r = app.get('/things')
        assert r.status_int == 200
        assert len(loads(r.body.decode())['items']) == 3

        # test "RESET" custom action
        r = app.request('/things', method='RESET')
        assert r.status_int == 200
        assert r.body == b_('RESET')

        # test "RESET" custom action with _method parameter
        r = app.get('/things?_method=RESET')
        assert r.status_int == 200
        assert r.body == b_('RESET')

        # test the "OPTIONS" custom action
        r = app.request('/things', method='OPTIONS')
        assert r.status_int == 200
        assert r.body == b_('OPTIONS')

        # test the "OPTIONS" custom action with the _method parameter
        r = app.post('/things', {'_method': 'OPTIONS'})
        assert r.status_int == 200
        assert r.body == b_('OPTIONS')

        # test the "other" custom action
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = app.request('/things/other', method='MISC', status=405)
            assert r.status_int == 405

        # test the "other" custom action with the _method parameter
        r = app.post('/things/other', {'_method': 'MISC'}, status=405)
        assert r.status_int == 405

        # test the "others" custom action
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = app.request('/things/others/', method='MISC')
            assert r.status_int == 200
            assert r.body == b_('OTHERS')

        # test the "others" custom action missing trailing slash
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = app.request('/things/others', method='MISC', status=302)
            assert r.status_int == 302

        # test the "others" custom action with the _method parameter
        r = app.get('/things/others/?_method=MISC')
        assert r.status_int == 200
        assert r.body == b_('OTHERS')

        # test an invalid custom action
        r = app.get('/things?_method=BAD', status=404)
        assert r.status_int == 404

        # test custom "GET" request "count"
        r = app.get('/things/count')
        assert r.status_int == 200
        assert r.body == b_('3')

        # test custom "GET" request "length"
        r = app.get('/things/1/length')
        assert r.status_int == 200
        assert r.body == b_(str(len('one')))

        # test custom "GET" request through subcontroller
        r = app.get('/things/others/echo?value=test')
        assert r.status_int == 200
        assert r.body == b_('test')

        # test custom "POST" request "length"
        r = app.post('/things/1/length', {'value': 'test'})
        assert r.status_int == 200
        assert r.body == b_(str(len('onetest')))

        # test custom "POST" request through subcontroller
        r = app.post('/things/others/echo', {'value': 'test'})
        assert r.status_int == 200
        assert r.body == b_('test')

    def test_getall_with_trailing_slash(self):

        class ThingsController(RestController):

            data = ['zero', 'one', 'two', 'three']

            @expose('json')
            def get_all(self):
                return dict(items=self.data)

        class RootController(object):
            things = ThingsController()

        # create the app
        app = TestApp(make_app(RootController()))

        # test get_all
        r = app.get('/things/')
        assert r.status_int == 200
        assert r.body == b_(dumps(dict(items=ThingsController.data)))

    def test_404_with_lookup(self):

        class LookupController(RestController):

            def __init__(self, _id):
                self._id = _id

            @expose()
            def get_all(self):
                return 'ID: %s' % self._id

        class ThingsController(RestController):

            @expose()
            def _lookup(self, _id, *remainder):
                return LookupController(_id), remainder

        class RootController(object):
            things = ThingsController()

        # create the app
        app = TestApp(make_app(RootController()))

        # these should 404
        for path in ('/things', '/things/'):
            r = app.get(path, expect_errors=True)
            assert r.status_int == 404

        r = app.get('/things/foo')
        assert r.status_int == 200
        assert r.body == b_('ID: foo')

    def test_getall_with_lookup(self):

        class LookupController(RestController):

            def __init__(self, _id):
                self._id = _id

            @expose()
            def get_all(self):
                return 'ID: %s' % self._id

        class ThingsController(RestController):

            data = ['zero', 'one', 'two', 'three']

            @expose()
            def _lookup(self, _id, *remainder):
                return LookupController(_id), remainder

            @expose('json')
            def get_all(self):
                return dict(items=self.data)

        class RootController(object):
            things = ThingsController()

        # create the app
        app = TestApp(make_app(RootController()))

        # test get_all
        for path in ('/things', '/things/'):
            r = app.get(path)
            assert r.status_int == 200
            assert r.body == b_(dumps(dict(items=ThingsController.data)))

        r = app.get('/things/foo')
        assert r.status_int == 200
        assert r.body == b_('ID: foo')

    def test_simple_nested_rest(self):

        class BarController(RestController):

            @expose()
            def post(self):
                return "BAR-POST"

            @expose()
            def delete(self, id_):
                return "BAR-%s" % id_

        class FooController(RestController):

            bar = BarController()

            @expose()
            def post(self):
                return "FOO-POST"

            @expose()
            def delete(self, id_):
                return "FOO-%s" % id_

        class RootController(object):
            foo = FooController()

        # create the app
        app = TestApp(make_app(RootController()))

        r = app.post('/foo')
        assert r.status_int == 200
        assert r.body == b_("FOO-POST")

        r = app.delete('/foo/1')
        assert r.status_int == 200
        assert r.body == b_("FOO-1")

        r = app.post('/foo/bar')
        assert r.status_int == 200
        assert r.body == b_("BAR-POST")

        r = app.delete('/foo/bar/2')
        assert r.status_int == 200
        assert r.body == b_("BAR-2")

    def test_complicated_nested_rest(self):

        class BarsController(RestController):

            data = [['zero-zero', 'zero-one'], ['one-zero', 'one-one']]

            @expose()
            def get_one(self, foo_id, id):
                return self.data[int(foo_id)][int(id)]

            @expose('json')
            def get_all(self, foo_id):
                return dict(items=self.data[int(foo_id)])

            @expose()
            def new(self, foo_id):
                return 'NEW FOR %s' % foo_id

            @expose()
            def post(self, foo_id, value):
                foo_id = int(foo_id)
                if len(self.data) < foo_id + 1:
                    self.data.extend([[]] * (foo_id - len(self.data) + 1))
                self.data[foo_id].append(value)
                response.status = 302
                return 'CREATED FOR %s' % foo_id

            @expose()
            def edit(self, foo_id, id):
                return 'EDIT %s' % self.data[int(foo_id)][int(id)]

            @expose()
            def put(self, foo_id, id, value):
                self.data[int(foo_id)][int(id)] = value
                return 'UPDATED'

            @expose()
            def get_delete(self, foo_id, id):
                return 'DELETE %s' % self.data[int(foo_id)][int(id)]

            @expose()
            def delete(self, foo_id, id):
                del self.data[int(foo_id)][int(id)]
                return 'DELETED'

        class FoosController(RestController):

            data = ['zero', 'one']

            bars = BarsController()

            @expose()
            def get_one(self, id):
                return self.data[int(id)]

            @expose('json')
            def get_all(self):
                return dict(items=self.data)

            @expose()
            def new(self):
                return 'NEW'

            @expose()
            def edit(self, id):
                return 'EDIT %s' % self.data[int(id)]

            @expose()
            def post(self, value):
                self.data.append(value)
                response.status = 302
                return 'CREATED'

            @expose()
            def put(self, id, value):
                self.data[int(id)] = value
                return 'UPDATED'

            @expose()
            def get_delete(self, id):
                return 'DELETE %s' % self.data[int(id)]

            @expose()
            def delete(self, id):
                del self.data[int(id)]
                return 'DELETED'

        class RootController(object):
            foos = FoosController()

        # create the app
        app = TestApp(make_app(RootController()))

        # test get_all
        r = app.get('/foos')
        assert r.status_int == 200
        assert r.body == b_(dumps(dict(items=FoosController.data)))

        # test nested get_all
        r = app.get('/foos/1/bars')
        assert r.status_int == 200
        assert r.body == b_(dumps(dict(items=BarsController.data[1])))

        # test get_one
        for i, value in enumerate(FoosController.data):
            r = app.get('/foos/%d' % i)
            assert r.status_int == 200
            assert r.body == b_(value)

        # test nested get_one
        for i, value in enumerate(FoosController.data):
            for j, value in enumerate(BarsController.data[i]):
                r = app.get('/foos/%s/bars/%s' % (i, j))
                assert r.status_int == 200
                assert r.body == b_(value)

        # test post
        r = app.post('/foos', {'value': 'two'})
        assert r.status_int == 302
        assert r.body == b_('CREATED')

        # make sure it works
        r = app.get('/foos/2')
        assert r.status_int == 200
        assert r.body == b_('two')

        # test nested post
        r = app.post('/foos/2/bars', {'value': 'two-zero'})
        assert r.status_int == 302
        assert r.body == b_('CREATED FOR 2')

        # make sure it works
        r = app.get('/foos/2/bars/0')
        assert r.status_int == 200
        assert r.body == b_('two-zero')

        # test edit
        r = app.get('/foos/1/edit')
        assert r.status_int == 200
        assert r.body == b_('EDIT one')

        # test nested edit
        r = app.get('/foos/1/bars/1/edit')
        assert r.status_int == 200
        assert r.body == b_('EDIT one-one')

        # test put
        r = app.put('/foos/2', {'value': 'TWO'})
        assert r.status_int == 200
        assert r.body == b_('UPDATED')

        # make sure it works
        r = app.get('/foos/2')
        assert r.status_int == 200
        assert r.body == b_('TWO')

        # test nested put
        r = app.put('/foos/2/bars/0', {'value': 'TWO-ZERO'})
        assert r.status_int == 200
        assert r.body == b_('UPDATED')

        # make sure it works
        r = app.get('/foos/2/bars/0')
        assert r.status_int == 200
        assert r.body == b_('TWO-ZERO')

        # test put with _method parameter and GET
        r = app.get('/foos/2?_method=put', {'value': 'TWO!'}, status=405)
        assert r.status_int == 405

        # make sure it works
        r = app.get('/foos/2')
        assert r.status_int == 200
        assert r.body == b_('TWO')

        # test nested put with _method parameter and GET
        r = app.get(
            '/foos/2/bars/0?_method=put',
            {'value': 'ZERO-TWO!'}, status=405
        )
        assert r.status_int == 405

        # make sure it works
        r = app.get('/foos/2/bars/0')
        assert r.status_int == 200
        assert r.body == b_('TWO-ZERO')

        # test put with _method parameter and POST
        r = app.post('/foos/2?_method=put', {'value': 'TWO!'})
        assert r.status_int == 200
        assert r.body == b_('UPDATED')

        # make sure it works
        r = app.get('/foos/2')
        assert r.status_int == 200
        assert r.body == b_('TWO!')

        # test nested put with _method parameter and POST
        r = app.post('/foos/2/bars/0?_method=put', {'value': 'TWO-ZERO!'})
        assert r.status_int == 200
        assert r.body == b_('UPDATED')

        # make sure it works
        r = app.get('/foos/2/bars/0')
        assert r.status_int == 200
        assert r.body == b_('TWO-ZERO!')

        # test get delete
        r = app.get('/foos/2/delete')
        assert r.status_int == 200
        assert r.body == b_('DELETE TWO!')

        # test nested get delete
        r = app.get('/foos/2/bars/0/delete')
        assert r.status_int == 200
        assert r.body == b_('DELETE TWO-ZERO!')

        # test nested delete
        r = app.delete('/foos/2/bars/0')
        assert r.status_int == 200
        assert r.body == b_('DELETED')

        # make sure it works
        r = app.get('/foos/2/bars')
        assert r.status_int == 200
        assert len(loads(r.body.decode())['items']) == 0

        # test delete
        r = app.delete('/foos/2')
        assert r.status_int == 200
        assert r.body == b_('DELETED')

        # make sure it works
        r = app.get('/foos')
        assert r.status_int == 200
        assert len(loads(r.body.decode())['items']) == 2

        # test nested delete with _method parameter and GET
        r = app.get('/foos/1/bars/1?_method=DELETE', status=405)
        assert r.status_int == 405

        # make sure it works
        r = app.get('/foos/1/bars')
        assert r.status_int == 200
        assert len(loads(r.body.decode())['items']) == 2

        # test delete with _method parameter and GET
        r = app.get('/foos/1?_method=DELETE', status=405)
        assert r.status_int == 405

        # make sure it works
        r = app.get('/foos')
        assert r.status_int == 200
        assert len(loads(r.body.decode())['items']) == 2

        # test nested delete with _method parameter and POST
        r = app.post('/foos/1/bars/1?_method=DELETE')
        assert r.status_int == 200
        assert r.body == b_('DELETED')

        # make sure it works
        r = app.get('/foos/1/bars')
        assert r.status_int == 200
        assert len(loads(r.body.decode())['items']) == 1

        # test delete with _method parameter and POST
        r = app.post('/foos/1?_method=DELETE')
        assert r.status_int == 200
        assert r.body == b_('DELETED')

        # make sure it works
        r = app.get('/foos')
        assert r.status_int == 200
        assert len(loads(r.body.decode())['items']) == 1

    def test_nested_get_all(self):

        class BarsController(RestController):

            @expose()
            def get_one(self, foo_id, id):
                return '4'

            @expose()
            def get_all(self, foo_id):
                return '3'

        class FoosController(RestController):

            bars = BarsController()

            @expose()
            def get_one(self, id):
                return '2'

            @expose()
            def get_all(self):
                return '1'

        class RootController(object):
            foos = FoosController()

        # create the app
        app = TestApp(make_app(RootController()))

        r = app.get('/foos/')
        assert r.status_int == 200
        assert r.body == b_('1')

        r = app.get('/foos/1/')
        assert r.status_int == 200
        assert r.body == b_('2')

        r = app.get('/foos/1/bars/')
        assert r.status_int == 200
        assert r.body == b_('3')

        r = app.get('/foos/1/bars/2/')
        assert r.status_int == 200
        assert r.body == b_('4')

        r = app.get('/foos/bars/', status=404)
        assert r.status_int == 404

        r = app.get('/foos/bars/1', status=404)
        assert r.status_int == 404

    def test_nested_get_all_with_lookup(self):

        class BarsController(RestController):

            @expose()
            def get_one(self, foo_id, id):
                return '4'

            @expose()
            def get_all(self, foo_id):
                return '3'

            @expose('json')
            def _lookup(self, id, *remainder):
                redirect('/lookup-hit/')

        class FoosController(RestController):

            bars = BarsController()

            @expose()
            def get_one(self, id):
                return '2'

            @expose()
            def get_all(self):
                return '1'

        class RootController(object):
            foos = FoosController()

        # create the app
        app = TestApp(make_app(RootController()))

        r = app.get('/foos/')
        assert r.status_int == 200
        assert r.body == b_('1')

        r = app.get('/foos/1/')
        assert r.status_int == 200
        assert r.body == b_('2')

        r = app.get('/foos/1/bars/')
        assert r.status_int == 200
        assert r.body == b_('3')

        r = app.get('/foos/1/bars/2/')
        assert r.status_int == 200
        assert r.body == b_('4')

        r = app.get('/foos/bars/')
        assert r.status_int == 302
        assert r.headers['Location'].endswith('/lookup-hit/')

        r = app.get('/foos/bars/1')
        assert r.status_int == 302
        assert r.headers['Location'].endswith('/lookup-hit/')

    def test_bad_rest(self):

        class ThingsController(RestController):
            pass

        class RootController(object):
            things = ThingsController()

        # create the app
        app = TestApp(make_app(RootController()))

        # test get_all
        r = app.get('/things', status=404)
        assert r.status_int == 404

        # test get_one
        r = app.get('/things/1', status=404)
        assert r.status_int == 404

        # test post
        r = app.post('/things', {'value': 'one'}, status=404)
        assert r.status_int == 404

        # test edit
        r = app.get('/things/1/edit', status=404)
        assert r.status_int == 404

        # test put
        r = app.put('/things/1', {'value': 'ONE'}, status=404)

        # test put with _method parameter and GET
        r = app.get('/things/1?_method=put', {'value': 'ONE!'}, status=405)
        assert r.status_int == 405

        # test put with _method parameter and POST
        r = app.post('/things/1?_method=put', {'value': 'ONE!'}, status=404)
        assert r.status_int == 404

        # test get delete
        r = app.get('/things/1/delete', status=404)
        assert r.status_int == 404

        # test delete
        r = app.delete('/things/1', status=404)
        assert r.status_int == 404

        # test delete with _method parameter and GET
        r = app.get('/things/1?_method=DELETE', status=405)
        assert r.status_int == 405

        # test delete with _method parameter and POST
        r = app.post('/things/1?_method=DELETE', status=404)
        assert r.status_int == 404

        # test "RESET" custom action
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = app.request('/things', method='RESET', status=404)
            assert r.status_int == 404

    def test_nested_rest_with_missing_intermediate_id(self):

        class BarsController(RestController):

            data = [['zero-zero', 'zero-one'], ['one-zero', 'one-one']]

            @expose('json')
            def get_all(self, foo_id):
                return dict(items=self.data[int(foo_id)])

        class FoosController(RestController):

            data = ['zero', 'one']

            bars = BarsController()

            @expose()
            def get_one(self, id):
                return self.data[int(id)]

            @expose('json')
            def get_all(self):
                return dict(items=self.data)

        class RootController(object):
            foos = FoosController()

        # create the app
        app = TestApp(make_app(RootController()))

        # test get_all
        r = app.get('/foos')
        self.assertEqual(r.status_int, 200)
        self.assertEqual(r.body, b_(dumps(dict(items=FoosController.data))))

        # test nested get_all
        r = app.get('/foos/1/bars')
        self.assertEqual(r.status_int, 200)
        self.assertEqual(r.body, b_(dumps(dict(items=BarsController.data[1]))))

        r = app.get('/foos/bars', expect_errors=True)
        self.assertEqual(r.status_int, 404)

    def test_custom_with_trailing_slash(self):

        class CustomController(RestController):

            _custom_actions = {
                'detail': ['GET'],
                'create': ['POST'],
                'update': ['PUT'],
                'remove': ['DELETE'],
            }

            @expose()
            def detail(self):
                return 'DETAIL'

            @expose()
            def create(self):
                return 'CREATE'

            @expose()
            def update(self, id):
                return id

            @expose()
            def remove(self, id):
                return id

        app = TestApp(make_app(CustomController()))

        r = app.get('/detail')
        assert r.status_int == 200
        assert r.body == b_('DETAIL')

        r = app.get('/detail/')
        assert r.status_int == 200
        assert r.body == b_('DETAIL')

        r = app.post('/create')
        assert r.status_int == 200
        assert r.body == b_('CREATE')

        r = app.post('/create/')
        assert r.status_int == 200
        assert r.body == b_('CREATE')

        r = app.put('/update/123')
        assert r.status_int == 200
        assert r.body == b_('123')

        r = app.put('/update/123/')
        assert r.status_int == 200
        assert r.body == b_('123')

        r = app.delete('/remove/456')
        assert r.status_int == 200
        assert r.body == b_('456')

        r = app.delete('/remove/456/')
        assert r.status_int == 200
        assert r.body == b_('456')

    def test_custom_delete(self):

        class OthersController(object):

            @expose()
            def index(self):
                return 'DELETE'

            @expose()
            def reset(self, id):
                return str(id)

        class ThingsController(RestController):

            others = OthersController()

            @expose()
            def delete_fail(self):
                abort(500)

        class RootController(object):
            things = ThingsController()

        # create the app
        app = TestApp(make_app(RootController()))

        # test bad delete
        r = app.delete('/things/delete_fail', status=405)
        assert r.status_int == 405

        # test bad delete with _method parameter and GET
        r = app.get('/things/delete_fail?_method=delete', status=405)
        assert r.status_int == 405

        # test bad delete with _method parameter and POST
        r = app.post('/things/delete_fail', {'_method': 'delete'}, status=405)
        assert r.status_int == 405

        # test custom delete without ID
        r = app.delete('/things/others/')
        assert r.status_int == 200
        assert r.body == b_('DELETE')

        # test custom delete without ID with _method parameter and GET
        r = app.get('/things/others/?_method=delete', status=405)
        assert r.status_int == 405

        # test custom delete without ID with _method parameter and POST
        r = app.post('/things/others/', {'_method': 'delete'})
        assert r.status_int == 200
        assert r.body == b_('DELETE')

        # test custom delete with ID
        r = app.delete('/things/others/reset/1')
        assert r.status_int == 200
        assert r.body == b_('1')

        # test custom delete with ID with _method parameter and GET
        r = app.get('/things/others/reset/1?_method=delete', status=405)
        assert r.status_int == 405

        # test custom delete with ID with _method parameter and POST
        r = app.post('/things/others/reset/1', {'_method': 'delete'})
        assert r.status_int == 200
        assert r.body == b_('1')

    def test_get_with_var_args(self):

        class OthersController(object):

            @expose()
            def index(self, one, two, three):
                return 'NESTED: %s, %s, %s' % (one, two, three)

        class ThingsController(RestController):

            others = OthersController()

            @expose()
            def get_one(self, *args):
                return ', '.join(args)

        class RootController(object):
            things = ThingsController()

        # create the app
        app = TestApp(make_app(RootController()))

        # test get request
        r = app.get('/things/one/two/three')
        assert r.status_int == 200
        assert r.body == b_('one, two, three')

        # test nested get request
        r = app.get('/things/one/two/three/others/')
        assert r.status_int == 200
        assert r.body == b_('NESTED: one, two, three')

    def test_sub_nested_rest(self):

        class BazsController(RestController):

            data = [[['zero-zero-zero']]]

            @expose()
            def get_one(self, foo_id, bar_id, id):
                return self.data[int(foo_id)][int(bar_id)][int(id)]

        class BarsController(RestController):

            data = [['zero-zero']]

            bazs = BazsController()

            @expose()
            def get_one(self, foo_id, id):
                return self.data[int(foo_id)][int(id)]

        class FoosController(RestController):

            data = ['zero']

            bars = BarsController()

            @expose()
            def get_one(self, id):
                return self.data[int(id)]

        class RootController(object):
            foos = FoosController()

        # create the app
        app = TestApp(make_app(RootController()))

        # test sub-nested get_one
        r = app.get('/foos/0/bars/0/bazs/0')
        assert r.status_int == 200
        assert r.body == b_('zero-zero-zero')

    def test_sub_nested_rest_with_overwrites(self):

        class FinalController(object):

            @expose()
            def index(self):
                return 'FINAL'

            @expose()
            def named(self):
                return 'NAMED'

        class BazsController(RestController):

            data = [[['zero-zero-zero']]]

            final = FinalController()

            @expose()
            def get_one(self, foo_id, bar_id, id):
                return self.data[int(foo_id)][int(bar_id)][int(id)]

            @expose()
            def post(self):
                return 'POST-GRAND-CHILD'

            @expose()
            def put(self, id):
                return 'PUT-GRAND-CHILD'

        class BarsController(RestController):

            data = [['zero-zero']]

            bazs = BazsController()

            @expose()
            def get_one(self, foo_id, id):
                return self.data[int(foo_id)][int(id)]

            @expose()
            def post(self):
                return 'POST-CHILD'

            @expose()
            def put(self, id):
                return 'PUT-CHILD'

        class FoosController(RestController):

            data = ['zero']

            bars = BarsController()

            @expose()
            def get_one(self, id):
                return self.data[int(id)]

            @expose()
            def post(self):
                return 'POST'

            @expose()
            def put(self, id):
                return 'PUT'

        class RootController(object):
            foos = FoosController()

        # create the app
        app = TestApp(make_app(RootController()))

        r = app.post('/foos')
        assert r.status_int == 200
        assert r.body == b_('POST')

        r = app.put('/foos/0')
        assert r.status_int == 200
        assert r.body == b_('PUT')

        r = app.post('/foos/bars')
        assert r.status_int == 200
        assert r.body == b_('POST-CHILD')

        r = app.put('/foos/bars/0')
        assert r.status_int == 200
        assert r.body == b_('PUT-CHILD')

        r = app.post('/foos/bars/bazs')
        assert r.status_int == 200
        assert r.body == b_('POST-GRAND-CHILD')

        r = app.put('/foos/bars/bazs/0')
        assert r.status_int == 200
        assert r.body == b_('PUT-GRAND-CHILD')

        r = app.get('/foos/bars/bazs/final/')
        assert r.status_int == 200
        assert r.body == b_('FINAL')

        r = app.get('/foos/bars/bazs/final/named')
        assert r.status_int == 200
        assert r.body == b_('NAMED')

    def test_post_with_kwargs_only(self):

        class RootController(RestController):

            @expose()
            def get_all(self):
                return 'INDEX'

            @expose('json')
            def post(self, **kw):
                return kw

        # create the app
        app = TestApp(make_app(RootController()))

        r = app.get('/')
        assert r.status_int == 200
        assert r.body == b_('INDEX')

        kwargs = {'foo': 'bar', 'spam': 'eggs'}
        r = app.post('/', kwargs)
        assert r.status_int == 200
        assert r.namespace['foo'] == 'bar'
        assert r.namespace['spam'] == 'eggs'

    def test_nested_rest_with_lookup(self):

        class SubController(RestController):

            @expose()
            def get_all(self):
                return "SUB"

        class FinalController(RestController):

            def __init__(self, id_):
                self.id_ = id_

            @expose()
            def get_all(self):
                return "FINAL-%s" % self.id_

            @expose()
            def post(self):
                return "POST-%s" % self.id_

        class LookupController(RestController):

            sub = SubController()

            def __init__(self, id_):
                self.id_ = id_

            @expose()
            def _lookup(self, id_, *remainder):
                return FinalController(id_), remainder

            @expose()
            def get_all(self):
                raise AssertionError("Never Reached")

            @expose()
            def post(self):
                return "POST-LOOKUP-%s" % self.id_

            @expose()
            def put(self, id_):
                return "PUT-LOOKUP-%s-%s" % (self.id_, id_)

            @expose()
            def delete(self, id_):
                return "DELETE-LOOKUP-%s-%s" % (self.id_, id_)

        class FooController(RestController):

            @expose()
            def _lookup(self, id_, *remainder):
                return LookupController(id_), remainder

            @expose()
            def get_one(self, id_):
                return "GET ONE"

            @expose()
            def get_all(self):
                return "INDEX"

            @expose()
            def post(self):
                return "POST"

            @expose()
            def put(self, id_):
                return "PUT-%s" % id_

            @expose()
            def delete(self, id_):
                return "DELETE-%s" % id_

        class RootController(RestController):
            foo = FooController()

        app = TestApp(make_app(RootController()))

        r = app.get('/foo')
        assert r.status_int == 200
        assert r.body == b_('INDEX')

        r = app.post('/foo')
        assert r.status_int == 200
        assert r.body == b_('POST')

        r = app.get('/foo/1')
        assert r.status_int == 200
        assert r.body == b_('GET ONE')

        r = app.post('/foo/1')
        assert r.status_int == 200
        assert r.body == b_('POST-LOOKUP-1')

        r = app.put('/foo/1')
        assert r.status_int == 200
        assert r.body == b_('PUT-1')

        r = app.delete('/foo/1')
        assert r.status_int == 200
        assert r.body == b_('DELETE-1')

        r = app.put('/foo/1/2')
        assert r.status_int == 200
        assert r.body == b_('PUT-LOOKUP-1-2')

        r = app.delete('/foo/1/2')
        assert r.status_int == 200
        assert r.body == b_('DELETE-LOOKUP-1-2')

        r = app.get('/foo/1/2')
        assert r.status_int == 200
        assert r.body == b_('FINAL-2')

        r = app.post('/foo/1/2')
        assert r.status_int == 200
        assert r.body == b_('POST-2')

    def test_nested_rest_with_default(self):

        class FooController(RestController):

            @expose()
            def _default(self, *remainder):
                return "DEFAULT %s" % remainder

        class RootController(RestController):
            foo = FooController()

        app = TestApp(make_app(RootController()))

        r = app.get('/foo/missing')
        assert r.status_int == 200
        assert r.body == b_("DEFAULT missing")

    def test_rest_with_non_utf_8_body(self):
        if PY3:
            # webob+PY3 doesn't suffer from this bug; the POST parsing in PY3
            # seems to more gracefully detect the bytestring
            return

        class FooController(RestController):

            @expose()
            def post(self):
                return "POST"

        class RootController(RestController):
            foo = FooController()

        app = TestApp(make_app(RootController()))

        data = struct.pack('255h', *range(0, 255))
        r = app.post('/foo/', data, expect_errors=True)
        assert r.status_int == 400

    def test_dynamic_rest_lookup(self):
        class BarController(RestController):
            @expose()
            def get_all(self):
                return "BAR"

            @expose()
            def put(self):
                return "PUT_BAR"

            @expose()
            def delete(self):
                return "DELETE_BAR"

        class BarsController(RestController):
            @expose()
            def _lookup(self, id_, *remainder):
                return BarController(), remainder

            @expose()
            def get_all(self):
                return "BARS"

            @expose()
            def post(self):
                return "POST_BARS"

        class FooController(RestController):
            bars = BarsController()

            @expose()
            def get_all(self):
                return "FOO"

            @expose()
            def put(self):
                return "PUT_FOO"

            @expose()
            def delete(self):
                return "DELETE_FOO"

        class FoosController(RestController):
            @expose()
            def _lookup(self, id_, *remainder):
                return FooController(), remainder

            @expose()
            def get_all(self):
                return "FOOS"

            @expose()
            def post(self):
                return "POST_FOOS"

        class RootController(RestController):
            foos = FoosController()

        app = TestApp(make_app(RootController()))

        r = app.get('/foos')
        assert r.status_int == 200
        assert r.body == b_('FOOS')

        r = app.post('/foos')
        assert r.status_int == 200
        assert r.body == b_('POST_FOOS')

        r = app.get('/foos/foo')
        assert r.status_int == 200
        assert r.body == b_('FOO')

        r = app.put('/foos/foo')
        assert r.status_int == 200
        assert r.body == b_('PUT_FOO')

        r = app.delete('/foos/foo')
        assert r.status_int == 200
        assert r.body == b_('DELETE_FOO')

        r = app.get('/foos/foo/bars')
        assert r.status_int == 200
        assert r.body == b_('BARS')

        r = app.post('/foos/foo/bars')
        assert r.status_int == 200
        assert r.body == b_('POST_BARS')

        r = app.get('/foos/foo/bars/bar')
        assert r.status_int == 200
        assert r.body == b_('BAR')

        r = app.put('/foos/foo/bars/bar')
        assert r.status_int == 200
        assert r.body == b_('PUT_BAR')

        r = app.delete('/foos/foo/bars/bar')
        assert r.status_int == 200
        assert r.body == b_('DELETE_BAR')
