from datetime           import datetime, date
from decimal            import Decimal
try:
    from simplejson     import loads
except:
    from json           import loads
from unittest           import TestCase

from pecan.jsonify      import jsonify, encode
from pecan              import Pecan, expose, request
from webtest            import TestApp
from webob.multidict    import MultiDict, UnicodeMultiDict

def make_person():
    class Person(object):
        def __init__(self, first_name, last_name):
            self.first_name = first_name
            self.last_name = last_name
    
        @property
        def name(self):
            return '%s %s' % (self.first_name, self.last_name)
    return Person


def test_simple_rule(): 
    Person = make_person()
    
    # create a Person instance
    p = Person('Jonathan', 'LaCour')
    
    # register a generic JSON rule
    @jsonify.when_type(Person)
    def jsonify_person(obj):
        return dict(
            name=obj.name
        )
    
    # encode the object using our new rule
    result = loads(encode(p))
    assert result['name'] == 'Jonathan LaCour'
    assert len(result) == 1


class TestJsonify(object):
    
    def test_simple_jsonify(self):
        Person = make_person()
        
        # register a generic JSON rule
        @jsonify.when_type(Person)
        def jsonify_person(obj):
            return dict(
                name=obj.name
            )
        
        class RootController(object):
            @expose('json')
            def index(self):
                # create a Person instance
                p = Person('Jonathan', 'LaCour')
                return p
        
        app = TestApp(Pecan(RootController()))

        r = app.get('/')
        assert r.status_int == 200
        assert loads(r.body) == {'name':'Jonathan LaCour'}

class TestJsonifyGenericEncoder(TestCase):
    def test_json_callable(self):
        class JsonCallable(object):
            def __init__(self, arg):
                self.arg = arg
            def __json__(self):
                return {"arg":self.arg}

        result = encode(JsonCallable('foo'))
        assert loads(result) == {'arg':'foo'}

    def test_datetime(self):
        today = date.today()
        now = datetime.now()

        result = encode(today)
        assert loads(result) == str(today)

        result = encode(now)
        assert loads(result) == str(now)

    def test_decimal(self):
        # XXX Testing for float match which is inexact

        d = Decimal('1.1')
        result = encode(d)
        assert loads(result) == float(d)

    def test_multidict(self):
        md = MultiDict()
        md.add('arg', 'foo')
        md.add('arg', 'bar')
        result = encode(md)
        assert loads(result) == {'arg': ['foo', 'bar']}

    def test_fallback_to_builtin_encoder(self):
        class Foo(object): pass

        self.assertRaises(TypeError, encode, Foo())
