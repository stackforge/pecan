from cStringIO import StringIO
from pecan import make_app, expose, redirect, abort
from pecan.core import state
from pecan.hooks import (
    PecanHook, TransactionHook, HookController, RequestViewerHook
)
from pecan.configuration import Config
from pecan.decorators import transactional, after_commit, after_rollback
from unittest import TestCase
from webtest import TestApp


class TestHooks(TestCase):

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
        assert response.body == 'Hello, World!'

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
        assert response.body == 'Hello, World!'

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
        assert response.body == 'Hello World!'

        assert len(run_hook) == 2
        assert run_hook[0] == 'on_route'
        assert run_hook[1] == 'inside'

        run_hook = []
        try:
            response = app.get('/causeerror')
        except Exception, e:
            assert isinstance(e, IndexError)

        assert len(run_hook) == 2
        assert run_hook[0] == 'on_route'
        assert run_hook[1] == 'error'

    def test_prioritized_hooks(self):
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

        papp = make_app(RootController(), hooks=[
            SimpleHook(1), SimpleHook(2), SimpleHook(3)
        ])
        app = TestApp(papp)
        response = app.get('/')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'

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

        run_hook = []

        state.app.hooks[0].priority = 3
        state.app.hooks[1].priority = 2
        state.app.hooks[2].priority = 1

        response = app.get('/')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'

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
        assert response.body == 'Hello, World!'

        assert len(run_hook) == 1
        assert run_hook[0] == 'inside'

        run_hook = []

        response = app.get('/sub/')
        assert response.status_int == 200
        assert response.body == 'Inside here!'

        assert len(run_hook) == 3
        assert run_hook[0] == 'before'
        assert run_hook[1] == 'inside_sub'
        assert run_hook[2] == 'after'

        run_hook = []
        response = app.get('/sub/sub/')
        assert response.status_int == 200
        assert response.body == 'Deep inside here!'

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
        assert response.body == 'Hello, World!'

        assert len(run_hook) == 4
        assert run_hook[0] == 'on_route1'
        assert run_hook[1] == 'before1'
        assert run_hook[2] == 'inside'
        assert run_hook[3] == 'after1'

        run_hook = []

        response = app.get('/sub/')
        assert response.status_int == 200
        assert response.body == 'Inside here!'

        assert len(run_hook) == 6
        assert run_hook[0] == 'on_route1'
        assert run_hook[1] == 'before2'
        assert run_hook[2] == 'before1'
        assert run_hook[3] == 'inside_sub'
        assert run_hook[4] == 'after1'
        assert run_hook[5] == 'after2'


class TestTransactionHook(TestCase):
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
        assert response.body == 'Hello, World!'

        assert len(run_hook) == 3
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'clear'

        run_hook = []

        response = app.post('/')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'

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
        assert response.body == 'Index Method!'

        assert len(run_hook) == 3
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'clear'

        run_hook = []

        response = app.post('/')
        assert response.status_int == 200
        assert response.body == 'Index Method!'

        assert len(run_hook) == 5
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'commit'
        assert run_hook[3] == 'action-one'
        assert run_hook[4] == 'clear'

        run_hook = []

        response = app.get('/decorated')
        assert response.status_int == 200
        assert response.body == 'Decorated Method!'

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
        assert response.body == 'Hello, World!'

        assert len(run_hook) == 3
        assert run_hook[0] == 'start_ro'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'clear'

        run_hook = []

        # test hooks for /

        response = app.post('/')
        assert response.status_int == 200
        assert response.body == 'Hello, World!'

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
        assert response.body == 'Hello, World!'

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
        assert response.body == 'Hello, World!'

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
        assert response.body == 'generic get'
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
        assert response.body == 'generic post'
        assert len(run_hook) == 4
        assert run_hook[0] == 'start'
        assert run_hook[1] == 'inside'
        assert run_hook[2] == 'commit'
        assert run_hook[3] == 'clear'


class TestRequestViewerHook(TestCase):

    def test_hook_from_config(self):
        from pecan.configuration import _runtime_conf as conf
        conf['requestviewer'] = {
            'blacklist': ['/favicon.ico']
        }

        class RootController(object):
            pass

        app = make_app(RootController())
        while hasattr(app, 'application'):
            app = app.application
        del conf.__values__['requestviewer']
        assert app.hooks

    def test_basic_single_default_hook(self):

        _stdout = StringIO()

        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'

        app = TestApp(
            make_app(
                RootController(), hooks=[RequestViewerHook(writer=_stdout)]
            )
        )
        response = app.get('/')

        out = _stdout.getvalue()

        assert response.status_int == 200
        assert response.body == 'Hello, World!'
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
                RootController(), hooks=[RequestViewerHook(writer=_stdout)]
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
            make_app(RootController(),
                hooks=[
                    RequestViewerHook(
                        config={'items':['path']}, writer=_stdout
                    )
                ]
            )
        )
        response = app.get('/')

        out = _stdout.getvalue()

        assert response.status_int == 200
        assert response.body == 'Hello, World!'
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
            make_app(RootController(),
                hooks=[
                    RequestViewerHook(
                        config={'blacklist':['/']}, writer=_stdout
                    )
                ]
            )
        )
        response = app.get('/')

        out = _stdout.getvalue()

        assert response.status_int == 200
        assert response.body == 'Hello, World!'
        assert out == ''

    def test_item_not_in_defaults(self):

        _stdout = StringIO()

        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'

        app = TestApp(
            make_app(RootController(),
                hooks=[
                    RequestViewerHook(
                        config={'items':['date']}, writer=_stdout
                    )
                ]
            )
        )
        response = app.get('/')

        out = _stdout.getvalue()

        assert response.status_int == 200
        assert response.body == 'Hello, World!'
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
