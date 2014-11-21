import inspect
import operator

from webtest import TestApp
from six import PY3
from six import b as b_
from six import u as u_
from six.moves import cStringIO as StringIO

from pecan import make_app, expose, redirect, abort, rest, Request, Response
from pecan.hooks import (
    PecanHook, TransactionHook, HookController, RequestViewerHook
)
from pecan.configuration import Config
from pecan.decorators import transactional, after_commit, after_rollback
from pecan.tests import PecanTestCase

# The `inspect.Arguments` namedtuple is different between PY2/3
kwargs = operator.attrgetter('varkw' if PY3 else 'keywords')


class TestHooks(PecanTestCase):

    def test_basic_single_hook(self):
        run_hook = []

        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'

        class SimpleHook(PecanHook):
            def on_route(self, state):
                run_hook.append('on_route')

            def before(self, state):
                run_hook.append('before')

            def after(self, state):
                run_hook.append('after')

            def on_error(self, state, e):
                run_hook.append('error')

        app = TestApp(make_app(RootController(), hooks=[SimpleHook()]))
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == b_('Hello, World!')

        assert len(run_hook) == 4
        assert run_hook[0] == 'on_route'
        assert run_hook[1] == 'before'
        assert run_hook[2] == 'inside'
        assert run_hook[3] == 'after'

    def test_basic_multi_hook(self):
        run_hook = []

        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'

        class SimpleHook(PecanHook):
            def __init__(self, id):
                self.id = str(id)

            def on_route(self, state):
                run_hook.append('on_route' + self.id)

            def before(self, state):
                run_hook.append('before' + self.id)

            def after(self, state):
                run_hook.append('after' + self.id)

            def on_error(self, state, e):
                run_hook.append('error' + self.id)

        app = TestApp(make_app(RootController(), hooks=[
            SimpleHook(1), SimpleHook(2), SimpleHook(3)
        ]))
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == b_('Hello, World!')

        assert len(run_hook) == 10
        assert run_hook[0] == 'on_route1'
        assert run_hook[1] == 'on_route2'
        assert run_hook[2] == 'on_route3'
        assert run_hook[3] == 'before1'
        assert run_hook[4] == 'before2'
        assert run_hook[5] == 'before3'
        assert run_hook[6] == 'inside'
        assert run_hook[7] == 'after3'
        assert run_hook[8] == 'after2'
        assert run_hook[9] == 'after1'

    def test_partial_hooks(self):
        run_hook = []

        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello World!'

            @expose()
            def causeerror(self):
                return [][1]

        class ErrorHook(PecanHook):
            def on_error(self, state, e):
                run_hook.append('error')

        class OnRouteHook(PecanHook):
            def on_route(self, state):
                run_hook.append('on_route')

        app = TestApp(make_app(RootController(), hooks=[
            ErrorHook(), OnRouteHook()
        ]))

        response = app.get('/')
        assert response.status_int == 200
        assert response.body == b_('Hello World!')

        assert len(run_hook) == 2
        assert run_hook[0] == 'on_route'
        assert run_hook[1] == 'inside'

        run_hook = []
        try:
            response = app.get('/causeerror')
        except Exception as e:
            assert isinstance(e, IndexError)

        assert len(run_hook) == 2
        assert run_hook[0] == 'on_route'
        assert run_hook[1] == 'error'

    def test_on_error_response_hook(self):
        run_hook = []

        class RootController(object):
            @expose()
            def causeerror(self):
                return [][1]

        class ErrorHook(PecanHook):
            def on_error(self, state, e):
                run_hook.append('error')

                r = Response()
                r.text = u_('on_error')

                return r

        app = TestApp(make_app(RootController(), hooks=[
            ErrorHook()
        ]))

        response = app.get('/causeerror')

        assert len(run_hook) == 1
        assert run_hook[0] == 'error'
        assert response.text == 'on_error'

    def test_prioritized_hooks(self):
        run_hook = []

        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'

        class SimpleHook(PecanHook):
            def __init__(self, id, priority=None):
                self.id = str(id)
                if priority:
                    self.priority = priority

            def on_route(self, state):
                run_hook.append('on_route' + self.id)

            def before(self, state):
                run_hook.append('before' + self.id)

            def after(self, state):
                run_hook.append('after' + self.id)

            def on_error(self, state, e):
                run_hook.append('error' + self.id)

        papp = make_app(RootController(), hooks=[
            SimpleHook(1, 3), SimpleHook(2, 2), SimpleHook(3, 1)
        ])
        app = TestApp(papp)
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == b_('Hello, World!')

        assert len(run_hook) == 10
        assert run_hook[0] == 'on_route3'
        assert run_hook[1] == 'on_route2'
        assert run_hook[2] == 'on_route1'
        assert run_hook[3] == 'before3'
        assert run_hook[4] == 'before2'
        assert run_hook[5] == 'before1'
        assert run_hook[6] == 'inside'
        assert run_hook[7] == 'after1'
        assert run_hook[8] == 'after2'
        assert run_hook[9] == 'after3'

    def test_basic_isolated_hook(self):
        run_hook = []

        class SimpleHook(PecanHook):
            def on_route(self, state):
                run_hook.append('on_route')

            def before(self, state):
                run_hook.append('before')

            def after(self, state):
                run_hook.append('after')

            def on_error(self, state, e):
                run_hook.append('error')

        class SubSubController(object):
            @expose()
            def index(self):
                run_hook.append('inside_sub_sub')
                return 'Deep inside here!'

        class SubController(HookController):
            __hooks__ = [SimpleHook()]

            @expose()
            def index(self):
                run_hook.append('inside_sub')
                return 'Inside here!'

            sub = SubSubController()

        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'

            sub = SubController()

        app = TestApp(make_app(RootController()))
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == b_('Hello, World!')

        assert len(run_hook) == 1
        assert run_hook[0] == 'inside'

        run_hook = []

        response = app.get('/sub/')
        assert response.status_int == 200
        assert response.body == b_('Inside here!')

        assert len(run_hook) == 3
        assert run_hook[0] == 'before'
        assert run_hook[1] == 'inside_sub'
        assert run_hook[2] == 'after'

        run_hook = []
        response = app.get('/sub/sub/')
        assert response.status_int == 200
        assert response.body == b_('Deep inside here!')

        assert len(run_hook) == 3
        assert run_hook[0] == 'before'
        assert run_hook[1] == 'inside_sub_sub'
        assert run_hook[2] == 'after'

    def test_isolated_hook_with_global_hook(self):
        run_hook = []

        class SimpleHook(PecanHook):
            def __init__(self, id):
                self.id = str(id)

            def on_route(self, state):
                run_hook.append('on_route' + self.id)

            def before(self, state):
                run_hook.append('before' + self.id)

            def after(self, state):
                run_hook.append('after' + self.id)

            def on_error(self, state, e):
                run_hook.append('error' + self.id)

        class SubController(HookController):
            __hooks__ = [SimpleHook(2)]

            @expose()
            def index(self):
                run_hook.append('inside_sub')
                return 'Inside here!'

        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'

            sub = SubController()

        app = TestApp(make_app(RootController(), hooks=[SimpleHook(1)]))
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == b_('Hello, World!')

        assert len(run_hook) == 4
        assert run_hook[0] == 'on_route1'
        assert run_hook[1] == 'before1'
        assert run_hook[2] == 'inside'
        assert run_hook[3] == 'after1'

        run_hook = []

        response = app.get('/sub/')
        assert response.status_int == 200
        assert response.body == b_('Inside here!')

        assert len(run_hook) == 6
        assert run_hook[0] == 'on_route1'
        assert run_hook[1] == 'before2'
        assert run_hook[2] == 'before1'
        assert run_hook[3] == 'inside_sub'
        assert run_hook[4] == 'after1'
        assert run_hook[5] == 'after2'

    def test_mixin_hooks(self):
        run_hook = []

        class HelperHook(PecanHook):
            priority = 2

            def before(self, state):
                run_hook.append('helper - before hook')

        # we'll use the same hook instance to avoid duplicate calls
        helper_hook = HelperHook()

        class LastHook(PecanHook):
            priority = 200

            def before(self, state):
                run_hook.append('last - before hook')

        class SimpleHook(PecanHook):
            priority = 1

            def before(self, state):
                run_hook.append('simple - before hook')

        class HelperMixin(object):
            __hooks__ = [helper_hook]

        class LastMixin(object):
            __hooks__ = [LastHook()]

        class SubController(HookController, HelperMixin):
            __hooks__ = [LastHook()]

            @expose()
            def index(self):
                return "This is sub controller!"

        class RootController(HookController, LastMixin):
            __hooks__ = [SimpleHook(), helper_hook]

            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'

            sub = SubController()

        papp = make_app(RootController())
        app = TestApp(papp)
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == b_('Hello, World!')

        assert len(run_hook) == 4
        assert run_hook[0] == 'simple - before hook', run_hook[0]
        assert run_hook[1] == 'helper - before hook', run_hook[1]
        assert run_hook[2] == 'last - before hook', run_hook[2]
        assert run_hook[3] == 'inside', run_hook[3]

        run_hook = []
        response = app.get('/sub/')
        assert response.status_int == 200
        assert response.body == b_('This is sub controller!')

        assert len(run_hook) == 4, run_hook
        assert run_hook[0] == 'simple - before hook', run_hook[0]
        assert run_hook[1] == 'helper - before hook', run_hook[1]
        assert run_hook[2] == 'last - before hook', run_hook[2]
        # LastHook is invoked once again -
        # for each different instance of the Hook in the two Controllers
        assert run_hook[3] == 'last - before hook', run_hook[3]


class TestStateAccess(PecanTestCase):

    def setUp(self):
        super(TestStateAccess, self).setUp()
        self.args = None

        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'

            @expose()
            def greet(self, name):
                return 'Hello, %s!' % name

            @expose()
            def greetmore(self, *args):
                return 'Hello, %s!' % args[0]

            @expose()
            def kwargs(self, **kw):
                return 'Hello, %s!' % kw['name']

            @expose()
            def mixed(self, first, second, *args):
                return 'Mixed'

        class SimpleHook(PecanHook):
            def before(inself, state):
                self.args = (state.controller, state.arguments)

        self.root = RootController()
        self.app = TestApp(make_app(self.root, hooks=[SimpleHook()]))

    def test_no_args(self):
        self.app.get('/')
        assert self.args[0] == self.root.index
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == []
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {}

    def test_single_arg(self):
        self.app.get('/greet/joe')
        assert self.args[0] == self.root.greet
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == ['joe']
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {}

    def test_single_vararg(self):
        self.app.get('/greetmore/joe')
        assert self.args[0] == self.root.greetmore
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == []
        assert self.args[1].varargs == ['joe']
        assert kwargs(self.args[1]) == {}

    def test_single_kw(self):
        self.app.get('/kwargs/?name=joe')
        assert self.args[0] == self.root.kwargs
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == []
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {'name': 'joe'}

    def test_single_kw_post(self):
        self.app.post('/kwargs/', params={'name': 'joe'})
        assert self.args[0] == self.root.kwargs
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == []
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {'name': 'joe'}

    def test_mixed_args(self):
        self.app.get('/mixed/foo/bar/spam/eggs')
        assert self.args[0] == self.root.mixed
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == ['foo', 'bar']
        assert self.args[1].varargs == ['spam', 'eggs']


class TestStateAccessWithoutThreadLocals(PecanTestCase):

    def setUp(self):
        super(TestStateAccessWithoutThreadLocals, self).setUp()
        self.args = None

        class RootController(object):
            @expose()
            def index(self, req, resp):
                return 'Hello, World!'

            @expose()
            def greet(self, req, resp, name):
                return 'Hello, %s!' % name

            @expose()
            def greetmore(self, req, resp, *args):
                return 'Hello, %s!' % args[0]

            @expose()
            def kwargs(self, req, resp, **kw):
                return 'Hello, %s!' % kw['name']

            @expose()
            def mixed(self, req, resp, first, second, *args):
                return 'Mixed'

        class SimpleHook(PecanHook):
            def before(inself, state):
                self.args = (state.controller, state.arguments)

        self.root = RootController()
        self.app = TestApp(make_app(
            self.root,
            hooks=[SimpleHook()],
            use_context_locals=False
        ))

    def test_no_args(self):
        self.app.get('/')
        assert self.args[0] == self.root.index
        assert isinstance(self.args[1], inspect.Arguments)
        assert len(self.args[1].args) == 2
        assert isinstance(self.args[1].args[0], Request)
        assert isinstance(self.args[1].args[1], Response)
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {}

    def test_single_arg(self):
        self.app.get('/greet/joe')
        assert self.args[0] == self.root.greet
        assert isinstance(self.args[1], inspect.Arguments)
        assert len(self.args[1].args) == 3
        assert isinstance(self.args[1].args[0], Request)
        assert isinstance(self.args[1].args[1], Response)
        assert self.args[1].args[2] == 'joe'
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {}

    def test_single_vararg(self):
        self.app.get('/greetmore/joe')
        assert self.args[0] == self.root.greetmore
        assert isinstance(self.args[1], inspect.Arguments)
        assert len(self.args[1].args) == 2
        assert isinstance(self.args[1].args[0], Request)
        assert isinstance(self.args[1].args[1], Response)
        assert self.args[1].varargs == ['joe']
        assert kwargs(self.args[1]) == {}

    def test_single_kw(self):
        self.app.get('/kwargs/?name=joe')
        assert self.args[0] == self.root.kwargs
        assert isinstance(self.args[1], inspect.Arguments)
        assert len(self.args[1].args) == 2
        assert isinstance(self.args[1].args[0], Request)
        assert isinstance(self.args[1].args[1], Response)
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {'name': 'joe'}

    def test_single_kw_post(self):
        self.app.post('/kwargs/', params={'name': 'joe'})
        assert self.args[0] == self.root.kwargs
        assert isinstance(self.args[1], inspect.Arguments)
        assert len(self.args[1].args) == 2
        assert isinstance(self.args[1].args[0], Request)
        assert isinstance(self.args[1].args[1], Response)
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {'name': 'joe'}

    def test_mixed_args(self):
        self.app.get('/mixed/foo/bar/spam/eggs')
        assert self.args[0] == self.root.mixed
        assert isinstance(self.args[1], inspect.Arguments)
        assert len(self.args[1].args) == 4
        assert isinstance(self.args[1].args[0], Request)
        assert isinstance(self.args[1].args[1], Response)
        assert self.args[1].args[2:] == ['foo', 'bar']
        assert self.args[1].varargs == ['spam', 'eggs']


class TestRestControllerStateAccess(PecanTestCase):

    def setUp(self):
        super(TestRestControllerStateAccess, self).setUp()
        self.args = None

        class RootController(rest.RestController):

            @expose()
            def _default(self, _id, *args, **kw):
                return 'Default'

            @expose()
            def get_all(self, **kw):
                return 'All'

            @expose()
            def get_one(self, _id, *args, **kw):
                return 'One'

            @expose()
            def post(self, *args, **kw):
                return 'POST'

            @expose()
            def put(self, _id, *args, **kw):
                return 'PUT'

            @expose()
            def delete(self, _id, *args, **kw):
                return 'DELETE'

        class SimpleHook(PecanHook):
            def before(inself, state):
                self.args = (state.controller, state.arguments)

        self.root = RootController()
        self.app = TestApp(make_app(self.root, hooks=[SimpleHook()]))

    def test_get_all(self):
        self.app.get('/')
        assert self.args[0] == self.root.get_all
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == []
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {}

    def test_get_all_with_kwargs(self):
        self.app.get('/?foo=bar')
        assert self.args[0] == self.root.get_all
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == []
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {'foo': 'bar'}

    def test_get_one(self):
        self.app.get('/1')
        assert self.args[0] == self.root.get_one
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == ['1']
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {}

    def test_get_one_with_varargs(self):
        self.app.get('/1/2/3')
        assert self.args[0] == self.root.get_one
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == ['1']
        assert self.args[1].varargs == ['2', '3']
        assert kwargs(self.args[1]) == {}

    def test_get_one_with_kwargs(self):
        self.app.get('/1?foo=bar')
        assert self.args[0] == self.root.get_one
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == ['1']
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {'foo': 'bar'}

    def test_post(self):
        self.app.post('/')
        assert self.args[0] == self.root.post
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == []
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {}

    def test_post_with_varargs(self):
        self.app.post('/foo/bar')
        assert self.args[0] == self.root.post
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == []
        assert self.args[1].varargs == ['foo', 'bar']
        assert kwargs(self.args[1]) == {}

    def test_post_with_kwargs(self):
        self.app.post('/', params={'foo': 'bar'})
        assert self.args[0] == self.root.post
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == []
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {'foo': 'bar'}

    def test_put(self):
        self.app.put('/1')
        assert self.args[0] == self.root.put
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == ['1']
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {}

    def test_put_with_method_argument(self):
        self.app.post('/1?_method=put')
        assert self.args[0] == self.root.put
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == ['1']
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {'_method': 'put'}

    def test_put_with_varargs(self):
        self.app.put('/1/2/3')
        assert self.args[0] == self.root.put
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == ['1']
        assert self.args[1].varargs == ['2', '3']
        assert kwargs(self.args[1]) == {}

    def test_put_with_kwargs(self):
        self.app.put('/1?foo=bar')
        assert self.args[0] == self.root.put
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == ['1']
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {'foo': 'bar'}

    def test_delete(self):
        self.app.delete('/1')
        assert self.args[0] == self.root.delete
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == ['1']
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {}

    def test_delete_with_method_argument(self):
        self.app.post('/1?_method=delete')
        assert self.args[0] == self.root.delete
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == ['1']
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {'_method': 'delete'}

    def test_delete_with_varargs(self):
        self.app.delete('/1/2/3')
        assert self.args[0] == self.root.delete
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == ['1']
        assert self.args[1].varargs == ['2', '3']
        assert kwargs(self.args[1]) == {}

    def test_delete_with_kwargs(self):
        self.app.delete('/1?foo=bar')
        assert self.args[0] == self.root.delete
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == ['1']
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {'foo': 'bar'}

    def test_post_with_invalid_method_kwarg(self):
        self.app.post('/1?_method=invalid')
        assert self.args[0] == self.root._default
        assert isinstance(self.args[1], inspect.Arguments)
        assert self.args[1].args == ['1']
        assert self.args[1].varargs == []
        assert kwargs(self.args[1]) == {'_method': 'invalid'}


class TestTransactionHook(PecanTestCase):
    def test_transaction_hook(self):
        run_hook = []

        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'

            @expose()
            def redirect(self):
                redirect('/')

            @expose()
            def error(self):
                return [][1]

        def gen(event):
            return lambda: run_hook.append(event)

        app = TestApp(make_app(RootController(), hooks=[
            TransactionHook(
                start=gen('start'),
                start_ro=gen('start_ro'),
                commit=gen('commit'),
                rollback=gen('rollback'),
                clear=gen('clear')
            )
        ]))

        response = app.get('/')
        assert response.status_int == 200
        assert response.body == b_('Hello, World!')

        assert len(run_hook) == 3
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'clear'

        run_hook = []

        response = app.post('/')
        assert response.status_int == 200
        assert response.body == b_('Hello, World!')

        assert len(run_hook) == 4
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'commit'
        assert run_hook[3] == 'clear'

        #
        # test hooks for GET /redirect
        # This controller should always be non-transactional
        #

        run_hook = []

        response = app.get('/redirect')
        assert response.status_int == 302
        assert len(run_hook) == 2
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'

        #
        # test hooks for POST /redirect
        # This controller should always be transactional,
        # even in the case of redirects
        #

        run_hook = []

        response = app.post('/redirect')
        assert response.status_int == 302
        assert len(run_hook) == 3
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'commit'
        assert run_hook[2] == 'clear'

        run_hook = []
        try:
            response = app.post('/error')
        except IndexError:
            pass

        assert len(run_hook) == 3
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'rollback'
        assert run_hook[2] == 'clear'

    def test_transaction_hook_with_after_actions(self):
        run_hook = []

        def action(name):
            def action_impl():
                run_hook.append(name)
            return action_impl

        class RootController(object):
            @expose()
            @after_commit(action('action-one'))
            def index(self):
                run_hook.append('inside')
                return 'Index Method!'

            @expose()
            @transactional()
            @after_commit(action('action-two'))
            def decorated(self):
                run_hook.append('inside')
                return 'Decorated Method!'

            @expose()
            @after_rollback(action('action-three'))
            def rollback(self):
                abort(500)

            @expose()
            @transactional()
            @after_rollback(action('action-four'))
            def rollback_decorated(self):
                abort(500)

        def gen(event):
            return lambda: run_hook.append(event)

        app = TestApp(make_app(RootController(), hooks=[
            TransactionHook(
                start=gen('start'),
                start_ro=gen('start_ro'),
                commit=gen('commit'),
                rollback=gen('rollback'),
                clear=gen('clear')
            )
        ]))

        response = app.get('/')
        assert response.status_int == 200
        assert response.body == b_('Index Method!')

        assert len(run_hook) == 3
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'clear'

        run_hook = []

        response = app.post('/')
        assert response.status_int == 200
        assert response.body == b_('Index Method!')

        assert len(run_hook) == 5
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'commit'
        assert run_hook[3] == 'action-one'
        assert run_hook[4] == 'clear'

        run_hook = []

        response = app.get('/decorated')
        assert response.status_int == 200
        assert response.body == b_('Decorated Method!')

        assert len(run_hook) == 7
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'
        assert run_hook[2] == 'start'
        assert run_hook[3] == 'inside'
        assert run_hook[4] == 'commit'
        assert run_hook[5] == 'action-two'
        assert run_hook[6] == 'clear'

        run_hook = []

        response = app.get('/rollback', expect_errors=True)
        assert response.status_int == 500

        assert len(run_hook) == 2
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'

        run_hook = []

        response = app.post('/rollback', expect_errors=True)
        assert response.status_int == 500

        assert len(run_hook) == 4
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'rollback'
        assert run_hook[2] == 'action-three'
        assert run_hook[3] == 'clear'

        run_hook = []

        response = app.get('/rollback_decorated', expect_errors=True)
        assert response.status_int == 500

        assert len(run_hook) == 6
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'
        assert run_hook[2] == 'start'
        assert run_hook[3] == 'rollback'
        assert run_hook[4] == 'action-four'
        assert run_hook[5] == 'clear'

        run_hook = []

        response = app.get('/fourohfour', status=404)
        assert response.status_int == 404

        assert len(run_hook) == 2
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'

    def test_transaction_hook_with_transactional_decorator(self):
        run_hook = []

        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'

            @expose()
            def redirect(self):
                redirect('/')

            @expose()
            @transactional()
            def redirect_transactional(self):
                redirect('/')

            @expose()
            @transactional(False)
            def redirect_rollback(self):
                redirect('/')

            @expose()
            def error(self):
                return [][1]

            @expose()
            @transactional(False)
            def error_rollback(self):
                return [][1]

            @expose()
            @transactional()
            def error_transactional(self):
                return [][1]

        def gen(event):
            return lambda: run_hook.append(event)

        app = TestApp(make_app(RootController(), hooks=[
            TransactionHook(
                start=gen('start'),
                start_ro=gen('start_ro'),
                commit=gen('commit'),
                rollback=gen('rollback'),
                clear=gen('clear')
            )
        ]))

        response = app.get('/')
        assert response.status_int == 200
        assert response.body == b_('Hello, World!')

        assert len(run_hook) == 3
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'clear'

        run_hook = []

        # test hooks for /

        response = app.post('/')
        assert response.status_int == 200
        assert response.body == b_('Hello, World!')

        assert len(run_hook) == 4
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'commit'
        assert run_hook[3] == 'clear'

        #
        # test hooks for GET /redirect
        # This controller should always be non-transactional
        #

        run_hook = []

        response = app.get('/redirect')
        assert response.status_int == 302
        assert len(run_hook) == 2
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'

        #
        # test hooks for POST /redirect
        # This controller should always be transactional,
        # even in the case of redirects
        #

        run_hook = []

        response = app.post('/redirect')
        assert response.status_int == 302
        assert len(run_hook) == 3
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'commit'
        assert run_hook[2] == 'clear'

        #
        # test hooks for GET /redirect_transactional
        # This controller should always be transactional,
        # even in the case of redirects
        #

        run_hook = []

        response = app.get('/redirect_transactional')
        assert response.status_int == 302
        assert len(run_hook) == 5
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'
        assert run_hook[2] == 'start'
        assert run_hook[3] == 'commit'
        assert run_hook[4] == 'clear'

        #
        # test hooks for POST /redirect_transactional
        # This controller should always be transactional,
        # even in the case of redirects
        #

        run_hook = []

        response = app.post('/redirect_transactional')
        assert response.status_int == 302
        assert len(run_hook) == 3
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'commit'
        assert run_hook[2] == 'clear'

        #
        # test hooks for GET /redirect_rollback
        # This controller should always be transactional,
        # *except* in the case of redirects
        #
        run_hook = []

        response = app.get('/redirect_rollback')
        assert response.status_int == 302
        assert len(run_hook) == 5
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'
        assert run_hook[2] == 'start'
        assert run_hook[3] == 'rollback'
        assert run_hook[4] == 'clear'

        #
        # test hooks for POST /redirect_rollback
        # This controller should always be transactional,
        # *except* in the case of redirects
        #

        run_hook = []

        response = app.post('/redirect_rollback')
        assert response.status_int == 302
        assert len(run_hook) == 3
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'rollback'
        assert run_hook[2] == 'clear'

        #
        # Exceptions (other than HTTPFound) should *always*
        # rollback no matter what
        #
        run_hook = []

        try:
            response = app.post('/error')
        except IndexError:
            pass

        assert len(run_hook) == 3
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'rollback'
        assert run_hook[2] == 'clear'

        run_hook = []

        try:
            response = app.get('/error')
        except IndexError:
            pass

        assert len(run_hook) == 2
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'

        run_hook = []

        try:
            response = app.post('/error_transactional')
        except IndexError:
            pass

        assert len(run_hook) == 3
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'rollback'
        assert run_hook[2] == 'clear'

        run_hook = []

        try:
            response = app.get('/error_transactional')
        except IndexError:
            pass

        assert len(run_hook) == 5
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'
        assert run_hook[2] == 'start'
        assert run_hook[3] == 'rollback'
        assert run_hook[4] == 'clear'

        run_hook = []

        try:
            response = app.post('/error_rollback')
        except IndexError:
            pass

        assert len(run_hook) == 3
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'rollback'
        assert run_hook[2] == 'clear'

        run_hook = []

        try:
            response = app.get('/error_rollback')
        except IndexError:
            pass

        assert len(run_hook) == 5
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'
        assert run_hook[2] == 'start'
        assert run_hook[3] == 'rollback'
        assert run_hook[4] == 'clear'

    def test_transaction_hook_with_transactional_class_decorator(self):
        run_hook = []

        @transactional()
        class RootController(object):
            @expose()
            def index(self):
                run_hook.append('inside')
                return 'Hello, World!'

            @expose()
            def redirect(self):
                redirect('/')

            @expose()
            @transactional(False)
            def redirect_rollback(self):
                redirect('/')

            @expose()
            def error(self):
                return [][1]

            @expose(generic=True)
            def generic(self):
                pass

            @generic.when(method='GET')
            def generic_get(self):
                run_hook.append('inside')
                return 'generic get'

            @generic.when(method='POST')
            def generic_post(self):
                run_hook.append('inside')
                return 'generic post'

        def gen(event):
            return lambda: run_hook.append(event)

        app = TestApp(make_app(RootController(), hooks=[
            TransactionHook(
                start=gen('start'),
                start_ro=gen('start_ro'),
                commit=gen('commit'),
                rollback=gen('rollback'),
                clear=gen('clear')
            )
        ]))

        response = app.get('/')
        assert response.status_int == 200
        assert response.body == b_('Hello, World!')

        assert len(run_hook) == 6
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'
        assert run_hook[2] == 'start'
        assert run_hook[3] == 'inside'
        assert run_hook[4] == 'commit'
        assert run_hook[5] == 'clear'

        run_hook = []

        # test hooks for /

        response = app.post('/')
        assert response.status_int == 200
        assert response.body == b_('Hello, World!')

        assert len(run_hook) == 4
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'commit'
        assert run_hook[3] == 'clear'

        #
        # test hooks for GET /redirect
        # This controller should always be transactional,
        # even in the case of redirects
        #

        run_hook = []
        response = app.get('/redirect')
        assert response.status_int == 302
        assert len(run_hook) == 5
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'
        assert run_hook[2] == 'start'
        assert run_hook[3] == 'commit'
        assert run_hook[4] == 'clear'

        #
        # test hooks for POST /redirect
        # This controller should always be transactional,
        # even in the case of redirects
        #

        run_hook = []

        response = app.post('/redirect')
        assert response.status_int == 302
        assert len(run_hook) == 3
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'commit'
        assert run_hook[2] == 'clear'

        #
        # test hooks for GET /redirect_rollback
        # This controller should always be transactional,
        # *except* in the case of redirects
        #
        run_hook = []

        response = app.get('/redirect_rollback')
        assert response.status_int == 302
        assert len(run_hook) == 5
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'
        assert run_hook[2] == 'start'
        assert run_hook[3] == 'rollback'
        assert run_hook[4] == 'clear'

        #
        # test hooks for POST /redirect_rollback
        # This controller should always be transactional,
        # *except* in the case of redirects
        #

        run_hook = []

        response = app.post('/redirect_rollback')
        assert response.status_int == 302
        assert len(run_hook) == 3
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'rollback'
        assert run_hook[2] == 'clear'

        #
        # Exceptions (other than HTTPFound) should *always*
        # rollback no matter what
        #
        run_hook = []

        try:
            response = app.post('/error')
        except IndexError:
            pass

        assert len(run_hook) == 3
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'rollback'
        assert run_hook[2] == 'clear'

        run_hook = []

        try:
            response = app.get('/error')
        except IndexError:
            pass

        assert len(run_hook) == 5
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'
        assert run_hook[2] == 'start'
        assert run_hook[3] == 'rollback'
        assert run_hook[4] == 'clear'

        #
        # test hooks for GET /generic
        # This controller should always be transactional,
        #

        run_hook = []

        response = app.get('/generic')
        assert response.status_int == 200
        assert response.body == b_('generic get')
        assert len(run_hook) == 6
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'clear'
        assert run_hook[2] == 'start'
        assert run_hook[3] == 'inside'
        assert run_hook[4] == 'commit'
        assert run_hook[5] == 'clear'

        #
        # test hooks for POST /generic
        # This controller should always be transactional,
        #

        run_hook = []

        response = app.post('/generic')
        assert response.status_int == 200
        assert response.body == b_('generic post')
        assert len(run_hook) == 4
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'commit'
        assert run_hook[3] == 'clear'

    def test_transaction_hook_with_broken_hook(self):
        """
        In a scenario where a preceding hook throws an exception,
        ensure that TransactionHook still rolls back properly.
        """
        run_hook = []

        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'

        def gen(event):
            return lambda: run_hook.append(event)

        class MyCustomException(Exception):
            pass

        class MyHook(PecanHook):

            def on_route(self, state):
                raise MyCustomException('BROKEN!')

        app = TestApp(make_app(RootController(), hooks=[
            MyHook(),
            TransactionHook(
                start=gen('start'),
                start_ro=gen('start_ro'),
                commit=gen('commit'),
                rollback=gen('rollback'),
                clear=gen('clear')
            )
        ]))

        self.assertRaises(
            MyCustomException,
            app.get,
            '/'
        )

        assert len(run_hook) == 1
        assert run_hook[0] == 'clear'


class TestRequestViewerHook(PecanTestCase):

    def test_basic_single_default_hook(self):

        _stdout = StringIO()

        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'

        app = TestApp(
            make_app(
                RootController(), hooks=lambda: [
                    RequestViewerHook(writer=_stdout)
                ]
            )
        )
        response = app.get('/')

        out = _stdout.getvalue()

        assert response.status_int == 200
        assert response.body == b_('Hello, World!')
        assert 'path' in out
        assert 'method' in out
        assert 'status' in out
        assert 'method' in out
        assert 'params' in out
        assert 'hooks' in out
        assert '200 OK' in out
        assert "['RequestViewerHook']" in out
        assert '/' in out

    def test_bad_response_from_app(self):
        """When exceptions are raised the hook deals with them properly"""

        _stdout = StringIO()

        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'

        app = TestApp(
            make_app(
                RootController(), hooks=lambda: [
                    RequestViewerHook(writer=_stdout)
                ]
            )
        )
        response = app.get('/404', expect_errors=True)

        out = _stdout.getvalue()

        assert response.status_int == 404
        assert 'path' in out
        assert 'method' in out
        assert 'status' in out
        assert 'method' in out
        assert 'params' in out
        assert 'hooks' in out
        assert '404 Not Found' in out
        assert "['RequestViewerHook']" in out
        assert '/' in out

    def test_single_item(self):

        _stdout = StringIO()

        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'

        app = TestApp(
            make_app(
                RootController(),
                hooks=lambda: [
                    RequestViewerHook(
                        config={'items': ['path']}, writer=_stdout
                    )
                ]
            )
        )
        response = app.get('/')

        out = _stdout.getvalue()

        assert response.status_int == 200
        assert response.body == b_('Hello, World!')
        assert '/' in out
        assert 'path' in out
        assert 'method' not in out
        assert 'status' not in out
        assert 'method' not in out
        assert 'params' not in out
        assert 'hooks' not in out
        assert '200 OK' not in out
        assert "['RequestViewerHook']" not in out

    def test_single_blacklist_item(self):

        _stdout = StringIO()

        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'

        app = TestApp(
            make_app(
                RootController(),
                hooks=lambda: [
                    RequestViewerHook(
                        config={'blacklist': ['/']}, writer=_stdout
                    )
                ]
            )
        )
        response = app.get('/')

        out = _stdout.getvalue()

        assert response.status_int == 200
        assert response.body == b_('Hello, World!')
        assert out == ''

    def test_item_not_in_defaults(self):

        _stdout = StringIO()

        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'

        app = TestApp(
            make_app(
                RootController(),
                hooks=lambda: [
                    RequestViewerHook(
                        config={'items': ['date']}, writer=_stdout
                    )
                ]
            )
        )
        response = app.get('/')

        out = _stdout.getvalue()

        assert response.status_int == 200
        assert response.body == b_('Hello, World!')
        assert 'date' in out
        assert 'method' not in out
        assert 'status' not in out
        assert 'method' not in out
        assert 'params' not in out
        assert 'hooks' not in out
        assert '200 OK' not in out
        assert "['RequestViewerHook']" not in out
        assert '/' not in out

    def test_hook_formatting(self):
        hooks = ['<pecan.hooks.RequestViewerHook object at 0x103a5f910>']
        viewer = RequestViewerHook()
        formatted = viewer.format_hooks(hooks)

        assert formatted == ['RequestViewerHook']

    def test_deal_with_pecan_configs(self):
        """If config comes from pecan.conf convert it to dict"""
        conf = Config(conf_dict={'items': ['url']})
        viewer = RequestViewerHook(conf)

        assert viewer.items == ['url']


class TestRestControllerWithHooks(PecanTestCase):

    def test_restcontroller_with_hooks(self):

        class SomeHook(PecanHook):

            def before(self, state):
                state.response.headers['X-Testing'] = 'XYZ'

        class BaseController(rest.RestController):

            @expose()
            def delete(self, _id):
                return 'Deleting %s' % _id

        class RootController(BaseController, HookController):

            __hooks__ = [SomeHook()]

            @expose()
            def get_all(self):
                return 'Hello, World!'

            @staticmethod
            def static(cls):
                return 'static'

            @property
            def foo(self):
                return 'bar'

            def testing123(self):
                return 'bar'

            unhashable = [1, 'two', 3]

        app = TestApp(
            make_app(
                RootController()
            )
        )

        response = app.get('/')
        assert response.status_int == 200
        assert response.body == b_('Hello, World!')
        assert response.headers['X-Testing'] == 'XYZ'

        response = app.delete('/100/')
        assert response.status_int == 200
        assert response.body == b_('Deleting 100')
        assert response.headers['X-Testing'] == 'XYZ'
