from pecan import expose, make_app, request, response
from pecan.rest import RestController
from webob import exc
from webtest import TestApp, AppError
from py.test import raises
from json import dumps, loads


class TestRestController(object):
    
    def test_basic_rest(self):
        class ThingsController(RestController):
            data = ['zero', 'one', 'two', 'three']
            
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
        
        class RootController(object):
            things = ThingsController()
        
        # create the app
        app = TestApp(make_app(RootController()))
        
        # test get_all
        r = app.get('/things')
        assert r.status_int == 200
        assert r.body == dumps(dict(items=ThingsController.data))
        
        # test get_one
        for i, value in enumerate(ThingsController.data):
            r = app.get('/things/%d' % i)
            assert r.status_int == 200
            assert r.body == value
        
        # test post
        r = app.post('/things', {'value':'four'})
        assert r.status_int == 302
        assert r.body == 'CREATED'
        
        # make sure it works
        r = app.get('/things/4')
        assert r.status_int == 200
        assert r.body == 'four'
        
        # test edit
        r = app.get('/things/3/edit')
        assert r.status_int == 200
        assert r.body == 'EDIT three'
        
        # test put
        r = app.put('/things/4', {'value':'FOUR'})
        assert r.status_int == 200
        assert r.body == 'UPDATED'
        
        # make sure it works
        r = app.get('/things/4')
        assert r.status_int == 200
        assert r.body == 'FOUR'
        
        # test put with _method parameter and GET
        r = app.get('/things/4?_method=put', {'value':'FOUR!'}, status=405)
        assert r.status_int == 405
        
        # make sure it works
        r = app.get('/things/4')
        assert r.status_int == 200
        assert r.body == 'FOUR'
        
        # test put with _method parameter and POST
        r = app.post('/things/4?_method=put', {'value':'FOUR!'})
        assert r.status_int == 200
        assert r.body == 'UPDATED'
        
        # make sure it works
        r = app.get('/things/4')
        assert r.status_int == 200
        assert r.body == 'FOUR!'
        
        # test get delete
        r = app.get('/things/4/delete')
        assert r.status_int == 200
        assert r.body == 'DELETE FOUR!'
        
        # test delete
        r = app.delete('/things/4')
        assert r.status_int == 200
        assert r.body == 'DELETED'
        
        # make sure it works
        r = app.get('/things')
        assert r.status_int == 200
        assert len(loads(r.body)['items']) == 4
        
        # test delete with _method parameter and GET
        r = app.get('/things/3?_method=DELETE', status=405)
        assert r.status_int == 405
        
        # make sure it works
        r = app.get('/things')
        assert r.status_int == 200
        assert len(loads(r.body)['items']) == 4
        
        # test delete with _method parameter and POST
        r = app.post('/things/3?_method=DELETE')
        assert r.status_int == 200
        assert r.body == 'DELETED'
        
        # make sure it works
        r = app.get('/things')
        assert r.status_int == 200
        assert len(loads(r.body)['items']) == 3
    
    def test_nested_rest(self):
        
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
        assert r.body == dumps(dict(items=FoosController.data))
        
        # test nested get_all
        r = app.get('/foos/1/bars')
        assert r.status_int == 200
        assert r.body == dumps(dict(items=BarsController.data[1]))
        
        # test get_one
        for i, value in enumerate(FoosController.data):
            r = app.get('/foos/%d' % i)
            assert r.status_int == 200
            assert r.body == value
        
        # test nested get_one
        for i, value in enumerate(FoosController.data):
            for j, value in enumerate(BarsController.data[i]):
                r = app.get('/foos/%s/bars/%s' % (i, j))
                assert r.status_int == 200
                assert r.body == value
        
        # test post
        r = app.post('/foos', {'value':'two'})
        assert r.status_int == 302
        assert r.body == 'CREATED'
        
        # make sure it works
        r = app.get('/foos/2')
        assert r.status_int == 200
        assert r.body == 'two'
        
        # test nested post
        r = app.post('/foos/2/bars', {'value':'two-zero'})
        assert r.status_int == 302
        assert r.body == 'CREATED FOR 2'
        
        # make sure it works
        r = app.get('/foos/2/bars/0')
        assert r.status_int == 200
        assert r.body == 'two-zero'
        
        # test edit
        r = app.get('/foos/1/edit')
        assert r.status_int == 200
        assert r.body == 'EDIT one'
        
        # test nested edit
        r = app.get('/foos/1/bars/1/edit')
        assert r.status_int == 200
        assert r.body == 'EDIT one-one'
        
        # test put
        r = app.put('/foos/2', {'value':'TWO'})
        assert r.status_int == 200
        assert r.body == 'UPDATED'
        
        # make sure it works
        r = app.get('/foos/2')
        assert r.status_int == 200
        assert r.body == 'TWO'
        
        # test nested put
        r = app.put('/foos/2/bars/0', {'value':'TWO-ZERO'})
        assert r.status_int == 200
        assert r.body == 'UPDATED'
        
        # make sure it works
        r = app.get('/foos/2/bars/0')
        assert r.status_int == 200
        assert r.body == 'TWO-ZERO'
        
        # test put with _method parameter and GET
        r = app.get('/foos/2?_method=put', {'value':'TWO!'}, status=405)
        assert r.status_int == 405
        
        # make sure it works
        r = app.get('/foos/2')
        assert r.status_int == 200
        assert r.body == 'TWO'
        
        # test nested put with _method parameter and GET
        r = app.get('/foos/2/bars/0?_method=put', {'value':'ZERO-TWO!'}, status=405)
        assert r.status_int == 405
        
        # make sure it works
        r = app.get('/foos/2/bars/0')
        assert r.status_int == 200
        assert r.body == 'TWO-ZERO'
        
        # test put with _method parameter and POST
        r = app.post('/foos/2?_method=put', {'value':'TWO!'})
        assert r.status_int == 200
        assert r.body == 'UPDATED'
        
        # make sure it works
        r = app.get('/foos/2')
        assert r.status_int == 200
        assert r.body == 'TWO!'
        
        # test nested put with _method parameter and POST
        r = app.post('/foos/2/bars/0?_method=put', {'value':'TWO-ZERO!'})
        assert r.status_int == 200
        assert r.body == 'UPDATED'
        
        # make sure it works
        r = app.get('/foos/2/bars/0')
        assert r.status_int == 200
        assert r.body == 'TWO-ZERO!'
        
        # test get delete
        r = app.get('/foos/2/delete')
        assert r.status_int == 200
        assert r.body == 'DELETE TWO!'
        
        # test nested get delete
        r = app.get('/foos/2/bars/0/delete')
        assert r.status_int == 200
        assert r.body == 'DELETE TWO-ZERO!'
        
        # test nested delete
        r = app.delete('/foos/2/bars/0')
        assert r.status_int == 200
        assert r.body == 'DELETED'
        
        # make sure it works
        r = app.get('/foos/2/bars')
        assert r.status_int == 200
        assert len(loads(r.body)['items']) == 0
        
        # test delete
        r = app.delete('/foos/2')
        assert r.status_int == 200
        assert r.body == 'DELETED'
        
        # make sure it works
        r = app.get('/foos')
        assert r.status_int == 200
        assert len(loads(r.body)['items']) == 2
        
        # test nested delete with _method parameter and GET
        r = app.get('/foos/1/bars/1?_method=DELETE', status=405)
        assert r.status_int == 405
        
        # make sure it works
        r = app.get('/foos/1/bars')
        assert r.status_int == 200
        assert len(loads(r.body)['items']) == 2
        
        # test delete with _method parameter and GET
        r = app.get('/foos/1?_method=DELETE', status=405)
        assert r.status_int == 405
        
        # make sure it works
        r = app.get('/foos')
        assert r.status_int == 200
        assert len(loads(r.body)['items']) == 2
        
        # test nested delete with _method parameter and POST
        r = app.post('/foos/1/bars/1?_method=DELETE')
        assert r.status_int == 200
        assert r.body == 'DELETED'
        
        # make sure it works
        r = app.get('/foos/1/bars')
        assert r.status_int == 200
        assert len(loads(r.body)['items']) == 1
        
        # test delete with _method parameter and POST
        r = app.post('/foos/1?_method=DELETE')
        assert r.status_int == 200
        assert r.body == 'DELETED'
        
        # make sure it works
        r = app.get('/foos')
        assert r.status_int == 200
        assert len(loads(r.body)['items']) == 1
