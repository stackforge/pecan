import time
from json import dumps, loads
import warnings

from webtest import TestApp
from six import b as b_
from six import u as u_
import webob
import mock

from pecan import Pecan, expose, abort, Request, Response
from pecan.rest import RestController
from pecan.hooks import PecanHook, HookController
from pecan.tests import PecanTestCase


class TestThreadingLocalUsage(PecanTestCase):

    @property
    def root(self):
        class RootController(object):
            @expose()
            def index(self, req, resp):
                assert isinstance(req, webob.BaseRequest)
                assert isinstance(resp, webob.Response)
                return 'Hello, World!'

            @expose()
            def warning(self):
                return ("This should be unroutable because (req, resp) are not"
                        " arguments.  It should raise a TypeError.")

            @expose(generic=True)
            def generic(self):
                return ("This should be unroutable because (req, resp) are not"
                        " arguments.  It should raise a TypeError.")

            @generic.when(method='PUT')
            def generic_put(self, _id):
                return ("This should be unroutable because (req, resp) are not"
                        " arguments.  It should raise a TypeError.")

        return RootController

    def test_locals_are_not_used(self):
        with mock.patch('threading.local', side_effect=AssertionError()):

            app = TestApp(Pecan(self.root(), use_context_locals=False))
            r = app.get('/')
            assert r.status_int == 200
            assert r.body == b_('Hello, World!')

            self.assertRaises(AssertionError, Pecan, self.root)

    def test_threadlocal_argument_warning(self):
        with mock.patch('threading.local', side_effect=AssertionError()):

            app = TestApp(Pecan(self.root(), use_context_locals=False))
            self.assertRaises(
                TypeError,
                app.get,
                '/warning/'
            )

    def test_threadlocal_argument_warning_on_generic(self):
        with mock.patch('threading.local', side_effect=AssertionError()):

            app = TestApp(Pecan(self.root(), use_context_locals=False))
            self.assertRaises(
                TypeError,
                app.get,
                '/generic/'
            )

    def test_threadlocal_argument_warning_on_generic_delegate(self):
        with mock.patch('threading.local', side_effect=AssertionError()):

            app = TestApp(Pecan(self.root(), use_context_locals=False))
            self.assertRaises(
                TypeError,
                app.put,
                '/generic/'
            )


class TestIndexRouting(PecanTestCase):

    @property
    def app_(self):
        class RootController(object):
            @expose()
            def index(self, req, resp):
                assert isinstance(req, webob.BaseRequest)
                assert isinstance(resp, webob.Response)
                return 'Hello, World!'

        return TestApp(Pecan(RootController(), use_context_locals=False))

    def test_empty_root(self):
        r = self.app_.get('/')
        assert r.status_int == 200
        assert r.body == b_('Hello, World!')

    def test_index(self):
        r = self.app_.get('/index')
        assert r.status_int == 200
        assert r.body == b_('Hello, World!')

    def test_index_html(self):
        r = self.app_.get('/index.html')
        assert r.status_int == 200
        assert r.body == b_('Hello, World!')


class TestManualResponse(PecanTestCase):

    def test_manual_response(self):

        class RootController(object):
            @expose()
            def index(self, req, resp):
                resp = webob.Response(resp.environ)
                resp.body = b_('Hello, World!')
                return resp

        app = TestApp(Pecan(RootController(), use_context_locals=False))
        r = app.get('/')
        assert r.body == b_('Hello, World!'), r.body


class TestDispatch(PecanTestCase):

    @property
    def app_(self):
        class SubSubController(object):
            @expose()
            def index(self, req, resp):
                assert isinstance(req, webob.BaseRequest)
                assert isinstance(resp, webob.Response)
                return '/sub/sub/'

            @expose()
            def deeper(self, req, resp):
                assert isinstance(req, webob.BaseRequest)
                assert isinstance(resp, webob.Response)
                return '/sub/sub/deeper'

        class SubController(object):
            @expose()
            def index(self, req, resp):
                assert isinstance(req, webob.BaseRequest)
                assert isinstance(resp, webob.Response)
                return '/sub/'

            @expose()
            def deeper(self, req, resp):
                assert isinstance(req, webob.BaseRequest)
                assert isinstance(resp, webob.Response)
                return '/sub/deeper'

            sub = SubSubController()

        class RootController(object):
            @expose()
            def index(self, req, resp):
                assert isinstance(req, webob.BaseRequest)
                assert isinstance(resp, webob.Response)
                return '/'

            @expose()
            def deeper(self, req, resp):
                assert isinstance(req, webob.BaseRequest)
                assert isinstance(resp, webob.Response)
                return '/deeper'

            sub = SubController()

        return TestApp(Pecan(RootController(), use_context_locals=False))

    def test_index(self):
        r = self.app_.get('/')
        assert r.status_int == 200
        assert r.body == b_('/')

    def test_one_level(self):
        r = self.app_.get('/deeper')
        assert r.status_int == 200
        assert r.body == b_('/deeper')

    def test_one_level_with_trailing(self):
        r = self.app_.get('/sub/')
        assert r.status_int == 200
        assert r.body == b_('/sub/')

    def test_two_levels(self):
        r = self.app_.get('/sub/deeper')
        assert r.status_int == 200
        assert r.body == b_('/sub/deeper')

    def test_two_levels_with_trailing(self):
        r = self.app_.get('/sub/sub/')
        assert r.status_int == 200

    def test_three_levels(self):
        r = self.app_.get('/sub/sub/deeper')
        assert r.status_int == 200
        assert r.body == b_('/sub/sub/deeper')


class TestLookups(PecanTestCase):

    @property
    def app_(self):
        class LookupController(object):
            def __init__(self, someID):
                self.someID = someID

            @expose()
            def index(self, req, resp):
                return '/%s' % self.someID

            @expose()
            def name(self, req, resp):
                return '/%s/name' % self.someID

        class RootController(object):
            @expose()
            def index(self, req, resp):
                return '/'

            @expose()
            def _lookup(self, someID, *remainder):
                return LookupController(someID), remainder

        return TestApp(Pecan(RootController(), use_context_locals=False))

    def test_index(self):
        r = self.app_.get('/')
        assert r.status_int == 200
        assert r.body == b_('/')

    def test_lookup(self):
        r = self.app_.get('/100/')
        assert r.status_int == 200
        assert r.body == b_('/100')

    def test_lookup_with_method(self):
        r = self.app_.get('/100/name')
        assert r.status_int == 200
        assert r.body == b_('/100/name')

    def test_lookup_with_wrong_argspec(self):
        class RootController(object):
            @expose()
            def _lookup(self, someID):
                return 'Bad arg spec'  # pragma: nocover

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            app = TestApp(Pecan(RootController(), use_context_locals=False))
            r = app.get('/foo/bar', expect_errors=True)
            assert r.status_int == 404


class TestCanonicalLookups(PecanTestCase):

    @property
    def app_(self):
        class LookupController(object):
            def __init__(self, someID):
                self.someID = someID

            @expose()
            def index(self, req, resp):
                return self.someID

        class UserController(object):
            @expose()
            def _lookup(self, someID, *remainder):
                return LookupController(someID), remainder

        class RootController(object):
            users = UserController()

        return TestApp(Pecan(RootController(), use_context_locals=False))

    def test_canonical_lookup(self):
        assert self.app_.get('/users', expect_errors=404).status_int == 404
        assert self.app_.get('/users/', expect_errors=404).status_int == 404
        assert self.app_.get('/users/100').status_int == 302
        assert self.app_.get('/users/100/').body == b_('100')


class TestControllerArguments(PecanTestCase):

    @property
    def app_(self):
        class RootController(object):
            @expose()
            def index(self, req, resp, id):
                return 'index: %s' % id

            @expose()
            def multiple(self, req, resp, one, two):
                return 'multiple: %s, %s' % (one, two)

            @expose()
            def optional(self, req, resp, id=None):
                return 'optional: %s' % str(id)

            @expose()
            def multiple_optional(self, req, resp, one=None, two=None,
                                  three=None):
                return 'multiple_optional: %s, %s, %s' % (one, two, three)

            @expose()
            def variable_args(self, req, resp, *args):
                return 'variable_args: %s' % ', '.join(args)

            @expose()
            def variable_kwargs(self, req, resp, **kwargs):
                data = [
                    '%s=%s' % (key, kwargs[key])
                    for key in sorted(kwargs.keys())
                ]
                return 'variable_kwargs: %s' % ', '.join(data)

            @expose()
            def variable_all(self, req, resp, *args, **kwargs):
                data = [
                    '%s=%s' % (key, kwargs[key])
                    for key in sorted(kwargs.keys())
                ]
                return 'variable_all: %s' % ', '.join(list(args) + data)

            @expose()
            def eater(self, req, resp, id, dummy=None, *args, **kwargs):
                data = [
                    '%s=%s' % (key, kwargs[key])
                    for key in sorted(kwargs.keys())
                ]
                return 'eater: %s, %s, %s' % (
                    id,
                    dummy,
                    ', '.join(list(args) + data)
                )

            @expose()
            def _route(self, args, request):
                if hasattr(self, args[0]):
                    return getattr(self, args[0]), args[1:]
                else:
                    return self.index, args

        return TestApp(Pecan(RootController(), use_context_locals=False))

    def test_required_argument(self):
        try:
            r = self.app_.get('/')
            assert r.status_int != 200  # pragma: nocover
        except Exception as ex:
            assert type(ex) == TypeError
            assert ex.args[0] in (
                "index() takes exactly 4 arguments (3 given)",
                "index() missing 1 required positional argument: 'id'"
            )  # this messaging changed in Python 3.3

    def test_single_argument(self):
        r = self.app_.get('/1')
        assert r.status_int == 200
        assert r.body == b_('index: 1')

    def test_single_argument_with_encoded_url(self):
        r = self.app_.get('/This%20is%20a%20test%21')
        assert r.status_int == 200
        assert r.body == b_('index: This is a test!')

    def test_two_arguments(self):
        r = self.app_.get('/1/dummy', status=404)
        assert r.status_int == 404

    def test_keyword_argument(self):
        r = self.app_.get('/?id=2')
        assert r.status_int == 200
        assert r.body == b_('index: 2')

    def test_keyword_argument_with_encoded_url(self):
        r = self.app_.get('/?id=This%20is%20a%20test%21')
        assert r.status_int == 200
        assert r.body == b_('index: This is a test!')

    def test_argument_and_keyword_argument(self):
        r = self.app_.get('/3?id=three')
        assert r.status_int == 200
        assert r.body == b_('index: 3')

    def test_encoded_argument_and_keyword_argument(self):
        r = self.app_.get('/This%20is%20a%20test%21?id=three')
        assert r.status_int == 200
        assert r.body == b_('index: This is a test!')

    def test_explicit_kwargs(self):
        r = self.app_.post('/', {'id': '4'})
        assert r.status_int == 200
        assert r.body == b_('index: 4')

    def test_path_with_explicit_kwargs(self):
        r = self.app_.post('/4', {'id': 'four'})
        assert r.status_int == 200
        assert r.body == b_('index: 4')

    def test_multiple_kwargs(self):
        r = self.app_.get('/?id=5&dummy=dummy')
        assert r.status_int == 200
        assert r.body == b_('index: 5')

    def test_kwargs_from_root(self):
        r = self.app_.post('/', {'id': '6', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == b_('index: 6')

        # multiple args

    def test_multiple_positional_arguments(self):
        r = self.app_.get('/multiple/one/two')
        assert r.status_int == 200
        assert r.body == b_('multiple: one, two')

    def test_multiple_positional_arguments_with_url_encode(self):
        r = self.app_.get('/multiple/One%20/Two%21')
        assert r.status_int == 200
        assert r.body == b_('multiple: One , Two!')

    def test_multiple_positional_arguments_with_kwargs(self):
        r = self.app_.get('/multiple?one=three&two=four')
        assert r.status_int == 200
        assert r.body == b_('multiple: three, four')

    def test_multiple_positional_arguments_with_url_encoded_kwargs(self):
        r = self.app_.get('/multiple?one=Three%20&two=Four%20%21')
        assert r.status_int == 200
        assert r.body == b_('multiple: Three , Four !')

    def test_positional_args_with_dictionary_kwargs(self):
        r = self.app_.post('/multiple', {'one': 'five', 'two': 'six'})
        assert r.status_int == 200
        assert r.body == b_('multiple: five, six')

    def test_positional_args_with_url_encoded_dictionary_kwargs(self):
        r = self.app_.post('/multiple', {'one': 'Five%20', 'two': 'Six%20%21'})
        assert r.status_int == 200
        assert r.body == b_('multiple: Five%20, Six%20%21')

        # optional arg
    def test_optional_arg(self):
        r = self.app_.get('/optional')
        assert r.status_int == 200
        assert r.body == b_('optional: None')

    def test_multiple_optional(self):
        r = self.app_.get('/optional/1')
        assert r.status_int == 200
        assert r.body == b_('optional: 1')

    def test_multiple_optional_url_encoded(self):
        r = self.app_.get('/optional/Some%20Number')
        assert r.status_int == 200
        assert r.body == b_('optional: Some Number')

    def test_multiple_optional_missing(self):
        r = self.app_.get('/optional/2/dummy', status=404)
        assert r.status_int == 404

    def test_multiple_with_kwargs(self):
        r = self.app_.get('/optional?id=2')
        assert r.status_int == 200
        assert r.body == b_('optional: 2')

    def test_multiple_with_url_encoded_kwargs(self):
        r = self.app_.get('/optional?id=Some%20Number')
        assert r.status_int == 200
        assert r.body == b_('optional: Some Number')

    def test_multiple_args_with_url_encoded_kwargs(self):
        r = self.app_.get('/optional/3?id=three')
        assert r.status_int == 200
        assert r.body == b_('optional: 3')

    def test_url_encoded_positional_args(self):
        r = self.app_.get('/optional/Some%20Number?id=three')
        assert r.status_int == 200
        assert r.body == b_('optional: Some Number')

    def test_optional_arg_with_kwargs(self):
        r = self.app_.post('/optional', {'id': '4'})
        assert r.status_int == 200
        assert r.body == b_('optional: 4')

    def test_optional_arg_with_url_encoded_kwargs(self):
        r = self.app_.post('/optional', {'id': 'Some%20Number'})
        assert r.status_int == 200
        assert r.body == b_('optional: Some%20Number')

    def test_multiple_positional_arguments_with_dictionary_kwargs(self):
        r = self.app_.post('/optional/5', {'id': 'five'})
        assert r.status_int == 200
        assert r.body == b_('optional: 5')

    def test_multiple_positional_url_encoded_arguments_with_kwargs(self):
        r = self.app_.post('/optional/Some%20Number', {'id': 'five'})
        assert r.status_int == 200
        assert r.body == b_('optional: Some Number')

    def test_optional_arg_with_multiple_kwargs(self):
        r = self.app_.get('/optional?id=6&dummy=dummy')
        assert r.status_int == 200
        assert r.body == b_('optional: 6')

    def test_optional_arg_with_multiple_url_encoded_kwargs(self):
        r = self.app_.get('/optional?id=Some%20Number&dummy=dummy')
        assert r.status_int == 200
        assert r.body == b_('optional: Some Number')

    def test_optional_arg_with_multiple_dictionary_kwargs(self):
        r = self.app_.post('/optional', {'id': '7', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == b_('optional: 7')

    def test_optional_arg_with_multiple_url_encoded_dictionary_kwargs(self):
        r = self.app_.post('/optional', {
            'id': 'Some%20Number',
            'dummy': 'dummy'
        })
        assert r.status_int == 200
        assert r.body == b_('optional: Some%20Number')

        # multiple optional args

    def test_multiple_optional_positional_args(self):
        r = self.app_.get('/multiple_optional')
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: None, None, None')

    def test_multiple_optional_positional_args_one_arg(self):
        r = self.app_.get('/multiple_optional/1')
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: 1, None, None')

    def test_multiple_optional_positional_args_one_url_encoded_arg(self):
        r = self.app_.get('/multiple_optional/One%21')
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: One!, None, None')

    def test_multiple_optional_positional_args_all_args(self):
        r = self.app_.get('/multiple_optional/1/2/3')
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: 1, 2, 3')

    def test_multiple_optional_positional_args_all_url_encoded_args(self):
        r = self.app_.get('/multiple_optional/One%21/Two%21/Three%21')
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: One!, Two!, Three!')

    def test_multiple_optional_positional_args_too_many_args(self):
        r = self.app_.get('/multiple_optional/1/2/3/dummy', status=404)
        assert r.status_int == 404

    def test_multiple_optional_positional_args_with_kwargs(self):
        r = self.app_.get('/multiple_optional?one=1')
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: 1, None, None')

    def test_multiple_optional_positional_args_with_url_encoded_kwargs(self):
        r = self.app_.get('/multiple_optional?one=One%21')
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: One!, None, None')

    def test_multiple_optional_positional_args_with_string_kwargs(self):
        r = self.app_.get('/multiple_optional/1?one=one')
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: 1, None, None')

    def test_multiple_optional_positional_args_with_encoded_str_kwargs(self):
        r = self.app_.get('/multiple_optional/One%21?one=one')
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: One!, None, None')

    def test_multiple_optional_positional_args_with_dict_kwargs(self):
        r = self.app_.post('/multiple_optional', {'one': '1'})
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: 1, None, None')

    def test_multiple_optional_positional_args_with_encoded_dict_kwargs(self):
        r = self.app_.post('/multiple_optional', {'one': 'One%21'})
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: One%21, None, None')

    def test_multiple_optional_positional_args_and_dict_kwargs(self):
        r = self.app_.post('/multiple_optional/1', {'one': 'one'})
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: 1, None, None')

    def test_multiple_optional_encoded_positional_args_and_dict_kwargs(self):
        r = self.app_.post('/multiple_optional/One%21', {'one': 'one'})
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: One!, None, None')

    def test_multiple_optional_args_with_multiple_kwargs(self):
        r = self.app_.get('/multiple_optional?one=1&two=2&three=3&four=4')
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: 1, 2, 3')

    def test_multiple_optional_args_with_multiple_encoded_kwargs(self):
        r = self.app_.get(
            '/multiple_optional?one=One%21&two=Two%21&three=Three%21&four=4'
        )
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: One!, Two!, Three!')

    def test_multiple_optional_args_with_multiple_dict_kwargs(self):
        r = self.app_.post(
            '/multiple_optional',
            {'one': '1', 'two': '2', 'three': '3', 'four': '4'}
        )
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: 1, 2, 3')

    def test_multiple_optional_args_with_multiple_encoded_dict_kwargs(self):
        r = self.app_.post(
            '/multiple_optional',
            {
                'one': 'One%21',
                'two': 'Two%21',
                'three': 'Three%21',
                'four': '4'
            }
        )
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: One%21, Two%21, Three%21')

    def test_multiple_optional_args_with_last_kwarg(self):
        r = self.app_.get('/multiple_optional?three=3')
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: None, None, 3')

    def test_multiple_optional_args_with_last_encoded_kwarg(self):
        r = self.app_.get('/multiple_optional?three=Three%21')
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: None, None, Three!')

    def test_multiple_optional_args_with_middle_arg(self):
        r = self.app_.get('/multiple_optional', {'two': '2'})
        assert r.status_int == 200
        assert r.body == b_('multiple_optional: None, 2, None')

    def test_variable_args(self):
        r = self.app_.get('/variable_args')
        assert r.status_int == 200
        assert r.body == b_('variable_args: ')

    def test_multiple_variable_args(self):
        r = self.app_.get('/variable_args/1/dummy')
        assert r.status_int == 200
        assert r.body == b_('variable_args: 1, dummy')

    def test_multiple_encoded_variable_args(self):
        r = self.app_.get('/variable_args/Testing%20One%20Two/Three%21')
        assert r.status_int == 200
        assert r.body == b_('variable_args: Testing One Two, Three!')

    def test_variable_args_with_kwargs(self):
        r = self.app_.get('/variable_args?id=2&dummy=dummy')
        assert r.status_int == 200
        assert r.body == b_('variable_args: ')

    def test_variable_args_with_dict_kwargs(self):
        r = self.app_.post('/variable_args', {'id': '3', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == b_('variable_args: ')

    def test_variable_kwargs(self):
        r = self.app_.get('/variable_kwargs')
        assert r.status_int == 200
        assert r.body == b_('variable_kwargs: ')

    def test_multiple_variable_kwargs(self):
        r = self.app_.get('/variable_kwargs/1/dummy', status=404)
        assert r.status_int == 404

    def test_multiple_variable_kwargs_with_explicit_kwargs(self):
        r = self.app_.get('/variable_kwargs?id=2&dummy=dummy')
        assert r.status_int == 200
        assert r.body == b_('variable_kwargs: dummy=dummy, id=2')

    def test_multiple_variable_kwargs_with_explicit_encoded_kwargs(self):
        r = self.app_.get(
            '/variable_kwargs?id=Two%21&dummy=This%20is%20a%20test'
        )
        assert r.status_int == 200
        assert r.body == b_('variable_kwargs: dummy=This is a test, id=Two!')

    def test_multiple_variable_kwargs_with_dict_kwargs(self):
        r = self.app_.post('/variable_kwargs', {'id': '3', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == b_('variable_kwargs: dummy=dummy, id=3')

    def test_multiple_variable_kwargs_with_encoded_dict_kwargs(self):
        r = self.app_.post(
            '/variable_kwargs',
            {'id': 'Three%21', 'dummy': 'This%20is%20a%20test'}
        )
        assert r.status_int == 200
        result = 'variable_kwargs: dummy=This%20is%20a%20test, id=Three%21'
        assert r.body == b_(result)

    def test_variable_all(self):
        r = self.app_.get('/variable_all')
        assert r.status_int == 200
        assert r.body == b_('variable_all: ')

    def test_variable_all_with_one_extra(self):
        r = self.app_.get('/variable_all/1')
        assert r.status_int == 200
        assert r.body == b_('variable_all: 1')

    def test_variable_all_with_two_extras(self):
        r = self.app_.get('/variable_all/2/dummy')
        assert r.status_int == 200
        assert r.body == b_('variable_all: 2, dummy')

    def test_variable_mixed(self):
        r = self.app_.get('/variable_all/3?month=1&day=12')
        assert r.status_int == 200
        assert r.body == b_('variable_all: 3, day=12, month=1')

    def test_variable_mixed_explicit(self):
        r = self.app_.get('/variable_all/4?id=four&month=1&day=12')
        assert r.status_int == 200
        assert r.body == b_('variable_all: 4, day=12, id=four, month=1')

    def test_variable_post(self):
        r = self.app_.post('/variable_all/5/dummy')
        assert r.status_int == 200
        assert r.body == b_('variable_all: 5, dummy')

    def test_variable_post_with_kwargs(self):
        r = self.app_.post('/variable_all/6', {'month': '1', 'day': '12'})
        assert r.status_int == 200
        assert r.body == b_('variable_all: 6, day=12, month=1')

    def test_variable_post_mixed(self):
        r = self.app_.post(
            '/variable_all/7',
            {'id': 'seven', 'month': '1', 'day': '12'}
        )
        assert r.status_int == 200
        assert r.body == b_('variable_all: 7, day=12, id=seven, month=1')

    def test_no_remainder(self):
        try:
            r = self.app_.get('/eater')
            assert r.status_int != 200  # pragma: nocover
        except Exception as ex:
            assert type(ex) == TypeError
            assert ex.args[0] in (
                "eater() takes at least 4 arguments (3 given)",
                "eater() missing 1 required positional argument: 'id'"
            )  # this messaging changed in Python 3.3

    def test_one_remainder(self):
        r = self.app_.get('/eater/1')
        assert r.status_int == 200
        assert r.body == b_('eater: 1, None, ')

    def test_two_remainders(self):
        r = self.app_.get('/eater/2/dummy')
        assert r.status_int == 200
        assert r.body == b_('eater: 2, dummy, ')

    def test_many_remainders(self):
        r = self.app_.get('/eater/3/dummy/foo/bar')
        assert r.status_int == 200
        assert r.body == b_('eater: 3, dummy, foo, bar')

    def test_remainder_with_kwargs(self):
        r = self.app_.get('/eater/4?month=1&day=12')
        assert r.status_int == 200
        assert r.body == b_('eater: 4, None, day=12, month=1')

    def test_remainder_with_many_kwargs(self):
        r = self.app_.get('/eater/5?id=five&month=1&day=12&dummy=dummy')
        assert r.status_int == 200
        assert r.body == b_('eater: 5, dummy, day=12, month=1')

    def test_post_remainder(self):
        r = self.app_.post('/eater/6')
        assert r.status_int == 200
        assert r.body == b_('eater: 6, None, ')

    def test_post_three_remainders(self):
        r = self.app_.post('/eater/7/dummy')
        assert r.status_int == 200
        assert r.body == b_('eater: 7, dummy, ')

    def test_post_many_remainders(self):
        r = self.app_.post('/eater/8/dummy/foo/bar')
        assert r.status_int == 200
        assert r.body == b_('eater: 8, dummy, foo, bar')

    def test_post_remainder_with_kwargs(self):
        r = self.app_.post('/eater/9', {'month': '1', 'day': '12'})
        assert r.status_int == 200
        assert r.body == b_('eater: 9, None, day=12, month=1')

    def test_post_many_remainders_with_many_kwargs(self):
        r = self.app_.post(
            '/eater/10',
            {'id': 'ten', 'month': '1', 'day': '12', 'dummy': 'dummy'}
        )
        assert r.status_int == 200
        assert r.body == b_('eater: 10, dummy, day=12, month=1')


class TestRestController(PecanTestCase):

    @property
    def app_(self):

        class OthersController(object):

            @expose()
            def index(self, req, resp):
                return 'OTHERS'

            @expose()
            def echo(self, req, resp, value):
                return str(value)

        class ThingsController(RestController):
            data = ['zero', 'one', 'two', 'three']

            _custom_actions = {'count': ['GET'], 'length': ['GET', 'POST']}

            others = OthersController()

            @expose()
            def get_one(self, req, resp, id):
                return self.data[int(id)]

            @expose('json')
            def get_all(self, req, resp):
                return dict(items=self.data)

            @expose()
            def length(self, req, resp, id, value=None):
                length = len(self.data[int(id)])
                if value:
                    length += len(value)
                return str(length)

            @expose()
            def post(self, req, resp, value):
                self.data.append(value)
                resp.status = 302
                return 'CREATED'

            @expose()
            def edit(self, req, resp, id):
                return 'EDIT %s' % self.data[int(id)]

            @expose()
            def put(self, req, resp, id, value):
                self.data[int(id)] = value
                return 'UPDATED'

            @expose()
            def get_delete(self, req, resp, id):
                return 'DELETE %s' % self.data[int(id)]

            @expose()
            def delete(self, req, resp, id):
                del self.data[int(id)]
                return 'DELETED'

            @expose()
            def reset(self, req, resp):
                return 'RESET'

            @expose()
            def post_options(self, req, resp):
                return 'OPTIONS'

            @expose()
            def options(self, req, resp):
                abort(500)

            @expose()
            def other(self, req, resp):
                abort(500)

        class RootController(object):
            things = ThingsController()

        # create the app
        return TestApp(Pecan(RootController(), use_context_locals=False))

    def test_get_all(self):
        r = self.app_.get('/things')
        assert r.status_int == 200
        assert r.body == b_(dumps(dict(items=['zero', 'one', 'two', 'three'])))

    def test_get_one(self):
        for i, value in enumerate(['zero', 'one', 'two', 'three']):
            r = self.app_.get('/things/%d' % i)
            assert r.status_int == 200
            assert r.body == b_(value)

    def test_post(self):
        r = self.app_.post('/things', {'value': 'four'})
        assert r.status_int == 302
        assert r.body == b_('CREATED')

    def test_custom_action(self):
        r = self.app_.get('/things/3/edit')
        assert r.status_int == 200
        assert r.body == b_('EDIT three')

    def test_put(self):
        r = self.app_.put('/things/3', {'value': 'THREE!'})
        assert r.status_int == 200
        assert r.body == b_('UPDATED')

    def test_put_with_method_parameter_and_get(self):
        r = self.app_.get('/things/3?_method=put', {'value': 'X'}, status=405)
        assert r.status_int == 405

    def test_put_with_method_parameter_and_post(self):
        r = self.app_.post('/things/3?_method=put', {'value': 'THREE!'})
        assert r.status_int == 200
        assert r.body == b_('UPDATED')

    def test_get_delete(self):
        r = self.app_.get('/things/3/delete')
        assert r.status_int == 200
        assert r.body == b_('DELETE three')

    def test_delete_method(self):
        r = self.app_.delete('/things/3')
        assert r.status_int == 200
        assert r.body == b_('DELETED')

    def test_delete_with_method_parameter(self):
        r = self.app_.get('/things/3?_method=DELETE', status=405)
        assert r.status_int == 405

    def test_delete_with_method_parameter_and_post(self):
        r = self.app_.post('/things/3?_method=DELETE')
        assert r.status_int == 200
        assert r.body == b_('DELETED')

    def test_custom_method_type(self):
        r = self.app_.request('/things', method='RESET')
        assert r.status_int == 200
        assert r.body == b_('RESET')

    def test_custom_method_type_with_method_parameter(self):
        r = self.app_.get('/things?_method=RESET')
        assert r.status_int == 200
        assert r.body == b_('RESET')

    def test_options(self):
        r = self.app_.request('/things', method='OPTIONS')
        assert r.status_int == 200
        assert r.body == b_('OPTIONS')

    def test_options_with_method_parameter(self):
        r = self.app_.post('/things', {'_method': 'OPTIONS'})
        assert r.status_int == 200
        assert r.body == b_('OPTIONS')

    def test_other_custom_action(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = self.app_.request('/things/other', method='MISC', status=405)
            assert r.status_int == 405

    def test_other_custom_action_with_method_parameter(self):
        r = self.app_.post('/things/other', {'_method': 'MISC'}, status=405)
        assert r.status_int == 405

    def test_nested_controller_with_trailing_slash(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = self.app_.request('/things/others/', method='MISC')
            assert r.status_int == 200
            assert r.body == b_('OTHERS')

    def test_nested_controller_without_trailing_slash(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = self.app_.request('/things/others', method='MISC', status=302)
            assert r.status_int == 302

    def test_invalid_custom_action(self):
        r = self.app_.get('/things?_method=BAD', status=405)
        assert r.status_int == 405

    def test_named_action(self):
        # test custom "GET" request "length"
        r = self.app_.get('/things/1/length')
        assert r.status_int == 200
        assert r.body == b_(str(len('one')))

    def test_named_nested_action(self):
        # test custom "GET" request through subcontroller
        r = self.app_.get('/things/others/echo?value=test')
        assert r.status_int == 200
        assert r.body == b_('test')

    def test_nested_post(self):
        # test custom "POST" request through subcontroller
        r = self.app_.post('/things/others/echo', {'value': 'test'})
        assert r.status_int == 200
        assert r.body == b_('test')


class TestHooks(PecanTestCase):

    def test_basic_single_hook(self):
        run_hook = []

        class RootController(object):
            @expose()
            def index(self, req, resp):
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

        app = TestApp(Pecan(
            RootController(),
            hooks=[SimpleHook()],
            use_context_locals=False
        ))
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
            def index(self, req, resp):
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

        app = TestApp(Pecan(RootController(), hooks=[
            SimpleHook(1), SimpleHook(2), SimpleHook(3)
        ], use_context_locals=False))
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
            def index(self, req, resp):
                run_hook.append('inside')
                return 'Hello World!'

            @expose()
            def causeerror(self, req, resp):
                return [][1]

        class ErrorHook(PecanHook):
            def on_error(self, state, e):
                run_hook.append('error')

        class OnRouteHook(PecanHook):
            def on_route(self, state):
                run_hook.append('on_route')

        app = TestApp(Pecan(RootController(), hooks=[
            ErrorHook(), OnRouteHook()
        ], use_context_locals=False))

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
            def causeerror(self, req, resp):
                return [][1]

        class ErrorHook(PecanHook):
            def on_error(self, state, e):
                run_hook.append('error')

                r = webob.Response()
                r.text = u_('on_error')

                return r

        app = TestApp(Pecan(RootController(), hooks=[
            ErrorHook()
        ], use_context_locals=False))

        response = app.get('/causeerror')

        assert len(run_hook) == 1
        assert run_hook[0] == 'error'
        assert response.text == 'on_error'

    def test_prioritized_hooks(self):
        run_hook = []

        class RootController(object):
            @expose()
            def index(self, req, resp):
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

        papp = Pecan(RootController(), hooks=[
            SimpleHook(1, 3), SimpleHook(2, 2), SimpleHook(3, 1)
        ], use_context_locals=False)
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
            def index(self, req, resp):
                run_hook.append('inside_sub_sub')
                return 'Deep inside here!'

        class SubController(HookController):
            __hooks__ = [SimpleHook()]

            @expose()
            def index(self, req, resp):
                run_hook.append('inside_sub')
                return 'Inside here!'

            sub = SubSubController()

        class RootController(object):
            @expose()
            def index(self, req, resp):
                run_hook.append('inside')
                return 'Hello, World!'

            sub = SubController()

        app = TestApp(Pecan(RootController(), use_context_locals=False))
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
            def index(self, req, resp):
                run_hook.append('inside_sub')
                return 'Inside here!'

        class RootController(object):
            @expose()
            def index(self, req, resp):
                run_hook.append('inside')
                return 'Hello, World!'

            sub = SubController()

        app = TestApp(Pecan(
            RootController(),
            hooks=[SimpleHook(1)],
            use_context_locals=False
        ))
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


class TestGeneric(PecanTestCase):

    @property
    def root(self):
        class RootController(object):

            def __init__(self, unique):
                self.unique = unique

            @expose(generic=True, template='json')
            def index(self, req, resp):
                assert self.__class__.__name__ == 'RootController'
                assert isinstance(req, Request)
                assert isinstance(resp, Response)
                assert self.unique == req.headers.get('X-Unique')
                return {'hello': 'world'}

            @index.when(method='POST', template='json')
            def index_post(self, req, resp):
                assert self.__class__.__name__ == 'RootController'
                assert isinstance(req, Request)
                assert isinstance(resp, Response)
                assert self.unique == req.headers.get('X-Unique')
                return req.json

            @expose(template='json')
            def echo(self, req, resp):
                assert self.__class__.__name__ == 'RootController'
                assert isinstance(req, Request)
                assert isinstance(resp, Response)
                assert self.unique == req.headers.get('X-Unique')
                return req.json

            @expose(template='json')
            def extra(self, req, resp, first, second):
                assert self.__class__.__name__ == 'RootController'
                assert isinstance(req, Request)
                assert isinstance(resp, Response)
                assert self.unique == req.headers.get('X-Unique')
                return {'first': first, 'second': second}

        return RootController

    def test_generics_with_im_self_default(self):
        uniq = str(time.time())
        with mock.patch('threading.local', side_effect=AssertionError()):
            app = TestApp(Pecan(self.root(uniq), use_context_locals=False))
            r = app.get('/', headers={'X-Unique': uniq})
            assert r.status_int == 200
            json_resp = loads(r.body.decode())
            assert json_resp['hello'] == 'world'

    def test_generics_with_im_self_with_method(self):
        uniq = str(time.time())
        with mock.patch('threading.local', side_effect=AssertionError()):
            app = TestApp(Pecan(self.root(uniq), use_context_locals=False))
            r = app.post_json('/', {'foo': 'bar'}, headers={'X-Unique': uniq})
            assert r.status_int == 200
            json_resp = loads(r.body.decode())
            assert json_resp['foo'] == 'bar'

    def test_generics_with_im_self_with_path(self):
        uniq = str(time.time())
        with mock.patch('threading.local', side_effect=AssertionError()):
            app = TestApp(Pecan(self.root(uniq), use_context_locals=False))
            r = app.post_json('/echo/', {'foo': 'bar'},
                              headers={'X-Unique': uniq})
            assert r.status_int == 200
            json_resp = loads(r.body.decode())
            assert json_resp['foo'] == 'bar'

    def test_generics_with_im_self_with_extra_args(self):
        uniq = str(time.time())
        with mock.patch('threading.local', side_effect=AssertionError()):
            app = TestApp(Pecan(self.root(uniq), use_context_locals=False))
            r = app.get('/extra/123/456', headers={'X-Unique': uniq})
            assert r.status_int == 200
            json_resp = loads(r.body.decode())
            assert json_resp['first'] == '123'
            assert json_resp['second'] == '456'
