from unittest import TestCase
from webtest import TestApp

import py.test


class TestRootController(TestCase):
    
    def setUp(self):
        self.app = TestApp(py.test.wsgi_app)
    
    def test_get(self):
        response = self.app.get('/')
        assert response.status_int == 200
    
    def test_get_not_found(self):
        response = self.app.get('/a/bogus/url', expect_errors=True)
        assert response.status_int == 404
