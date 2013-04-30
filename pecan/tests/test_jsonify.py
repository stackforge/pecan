from datetime import datetime, date
from decimal import Decimal
try:
    from simplejson import loads
except:
    from json import loads  # noqa
try:
    from sqlalchemy import orm, schema, types
    from sqlalchemy.engine import create_engine
except ImportError:
    create_engine = None  # noqa

from webtest import TestApp
from webob.multidict import MultiDict

from pecan.jsonify import jsonify, encode, ResultProxy, RowProxy
from pecan import Pecan, expose
from pecan.tests import PecanTestCase


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


class TestJsonify(PecanTestCase):

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
        assert loads(r.body.decode()) == {'name': 'Jonathan LaCour'}


class TestJsonifyGenericEncoder(PecanTestCase):
    def test_json_callable(self):
        class JsonCallable(object):
            def __init__(self, arg):
                self.arg = arg

            def __json__(self):
                return {"arg": self.arg}

        result = encode(JsonCallable('foo'))
        assert loads(result) == {'arg': 'foo'}

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
        class Foo(object):
            pass

        self.assertRaises(TypeError, encode, Foo())


class TestJsonifySQLAlchemyGenericEncoder(PecanTestCase):

    def setUp(self):
        super(TestJsonifySQLAlchemyGenericEncoder, self).setUp()
        if not create_engine:
            self.create_fake_proxies()
        else:
            self.create_sa_proxies()

    def create_fake_proxies(self):

        # create a fake SA object
        class FakeSAObject(object):
            def __init__(self):
                self._sa_class_manager = object()
                self._sa_instance_state = 'awesome'
                self.id = 1
                self.first_name = 'Jonathan'
                self.last_name = 'LaCour'

        # create a fake result proxy
        class FakeResultProxy(ResultProxy):
            def __init__(self):
                self.rowcount = -1
                self.rows = []

            def __iter__(self):
                return iter(self.rows)

            def append(self, row):
                self.rows.append(row)

        # create a fake row proxy
        class FakeRowProxy(RowProxy):
            def __init__(self, arg=None):
                self.row = dict(arg)

            def __getitem__(self, key):
                return self.row.__getitem__(key)

            def keys(self):
                return self.row.keys()

        # get the SA objects
        self.sa_object = FakeSAObject()
        self.result_proxy = FakeResultProxy()
        self.result_proxy.append(
            FakeRowProxy([
                ('id', 1),
                ('first_name', 'Jonathan'),
                ('last_name', 'LaCour')
            ])
        )
        self.result_proxy.append(
            FakeRowProxy([
                ('id', 2), ('first_name', 'Yoann'), ('last_name', 'Roman')
            ]))
        self.row_proxy = FakeRowProxy([
            ('id', 1), ('first_name', 'Jonathan'), ('last_name', 'LaCour')
        ])

    def create_sa_proxies(self):

        # create the table and mapper
        metadata = schema.MetaData()
        user_table = schema.Table(
            'user',
            metadata,
            schema.Column('id', types.Integer, primary_key=True),
            schema.Column('first_name', types.Unicode(25)),
            schema.Column('last_name', types.Unicode(25))
        )

        class User(object):
            pass
        orm.mapper(User, user_table)

        # create the session
        engine = create_engine('sqlite:///:memory:')
        metadata.bind = engine
        metadata.create_all()
        session = orm.sessionmaker(bind=engine)()

        # add some dummy data
        user_table.insert().execute([
            {'first_name': 'Jonathan', 'last_name': 'LaCour'},
            {'first_name': 'Yoann', 'last_name': 'Roman'}
        ])

        # get the SA objects
        self.sa_object = session.query(User).first()
        select = user_table.select()
        self.result_proxy = select.execute()
        self.row_proxy = select.execute().fetchone()

    def test_sa_object(self):
        result = encode(self.sa_object)
        assert loads(result) == {
            'id': 1, 'first_name': 'Jonathan', 'last_name': 'LaCour'
        }

    def test_result_proxy(self):
        result = encode(self.result_proxy)
        assert loads(result) == {'count': 2, 'rows': [
            {'id': 1, 'first_name': 'Jonathan', 'last_name': 'LaCour'},
            {'id': 2, 'first_name': 'Yoann', 'last_name': 'Roman'}
        ]}

    def test_row_proxy(self):
        result = encode(self.row_proxy)
        assert loads(result) == {
            'id': 1, 'first_name': 'Jonathan', 'last_name': 'LaCour'
        }
