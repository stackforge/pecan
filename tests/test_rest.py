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
            
            @expose('json')
            def get_one(self, id):
                return self.data[int(id)]

            @expose('json')
            def get_all(self):
                return dict(items=self.data)
                
            @expose('json')
            def post(self, value):
                self.data.append(value)
                response.status = 302
                return 'CREATED'

            @expose('json')
            def put(self, id, value):
                self.data[int(id)] = value
                return 'UPDATED'
            
            @expose('json')
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
            assert r.body == dumps(value)
        
        # test post
        r = app.post('/things', {'value':'four'})
        assert r.status_int == 302
        assert r.body == dumps('CREATED')
        
        # make sure it works
        r = app.get('/things/4')
        assert r.status_int == 200
        assert r.body == dumps('four')
        
        # test put
        r = app.put('/things/4', {'value':'FOUR'})
        assert r.status_int == 200
        assert r.body == dumps('UPDATED')
        
        # make sure it works
        r = app.get('/things/4')
        assert r.status_int == 200
        assert r.body == dumps('FOUR')
        
        # test delete
        r = app.delete('/things/4')
        assert r.status_int == 200
        assert r.body == dumps('DELETED')
        
        # make sure it works
        r = app.get('/things')
        assert r.status_int == 200
        assert len(loads(r.body)['items']) == 4