import sys
import os
import json
import warnings
if sys.version_info < (2, 7):
    import unittest2 as unittest  # pragma: nocover
else:
    import unittest  # pragma: nocover

import webob
from webob.exc import HTTPNotFound
from webtest import TestApp
import six
from six import b as b_
from six import u as u_
from six.moves import cStringIO as StringIO

from pecan import (
    Pecan, Request, Response, expose, request, response, redirect,
    abort, make_app, override_template, render
)
from pecan.templating import (
    _builtin_renderers as builtin_renderers, error_formatters
)
from pecan.decorators import accept_noncanonical
from pecan.tests import PecanTestCase


class SampleRootController(object):
    pass


class TestAppRoot(PecanTestCase):

    def test_controller_lookup_by_string_path(self):
        app = Pecan('pecan.tests.test_base.SampleRootController')
        assert app.root and isinstance(app.root, SampleRootController)


class TestEmptyContent(PecanTestCase):
    @property
    def app_(self):
        class RootController(object):
            @expose()
            def index(self):
                pass

            @expose()
            def explicit_body(self):
                response.body = b_('Hello, World!')

            @expose()
            def empty_body(self):
                response.body = b_('')

            @expose()
            def explicit_text(self):
                response.text = six.text_type('Hello, World!')

            @expose()
            def empty_text(self):
                response.text = six.text_type('')

            @expose()
            def explicit_json(self):
                response.json = {'foo': 'bar'}

            @expose()
            def explicit_json_body(self):
                response.json_body = {'foo': 'bar'}

            @expose()
            def non_unicode(self):
                return chr(0xc0)

        return TestApp(Pecan(RootController()))

    def test_empty_index(self):
        r = self.app_.get('/')
        self.assertEqual(r.status_int, 204)
        self.assertNotIn('Content-Type', r.headers)
        self.assertEqual(r.headers['Content-Length'], '0')
        self.assertEqual(len(r.body), 0)

    def test_index_with_non_unicode(self):
        r = self.app_.get('/non_unicode/')
        self.assertEqual(r.status_int, 200)

    def test_explicit_body(self):
        r = self.app_.get('/explicit_body/')
        self.assertEqual(r.status_int, 200)
        self.assertEqual(r.body, b_('Hello, World!'))

    def test_empty_body(self):
        r = self.app_.get('/empty_body/')
        self.assertEqual(r.status_int, 204)
        self.assertEqual(r.body, b_(''))

    def test_explicit_text(self):
        r = self.app_.get('/explicit_text/')
        self.assertEqual(r.status_int, 200)
        self.assertEqual(r.body, b_('Hello, World!'))

    def test_empty_text(self):
        r = self.app_.get('/empty_text/')
        self.assertEqual(r.status_int, 204)
        self.assertEqual(r.body, b_(''))

    def test_explicit_json(self):
        r = self.app_.get('/explicit_json/')
        self.assertEqual(r.status_int, 200)
        json_resp = json.loads(r.body.decode())
        assert json_resp == {'foo': 'bar'}

    def test_explicit_json_body(self):
        r = self.app_.get('/explicit_json_body/')
        self.assertEqual(r.status_int, 200)
        json_resp = json.loads(r.body.decode())
        assert json_resp == {'foo': 'bar'}


class TestAppIterFile(PecanTestCase):
    @property
    def app_(self):
        class RootController(object):
            @expose()
            def index(self):
                body = six.BytesIO(b_('Hello, World!'))
                response.body_file = body

            @expose()
            def empty(self):
                body = six.BytesIO(b_(''))
                response.body_file = body

        return TestApp(Pecan(RootController()))

    def test_body_generator(self):
        r = self.app_.get('/')
        self.assertEqual(r.status_int, 200)
        assert r.body == b_('Hello, World!')

    def test_empty_body_generator(self):
        r = self.app_.get('/empty')
        self.assertEqual(r.status_int, 204)
        assert len(r.body) == 0


class TestInvalidURLEncoding(PecanTestCase):

    @property
    def app_(self):
        class RootController(object):

            @expose()
            def _route(self, args, request):
                assert request.path

        return TestApp(Pecan(RootController()))

    def test_rest_with_non_utf_8_body(self):
        r = self.app_.get('/%aa/', expect_errors=True)
        assert r.status_int == 400


class TestIndexRouting(PecanTestCase):

    @property
    def app_(self):
        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'

        return TestApp(Pecan(RootController()))

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


class TestObjectDispatch(PecanTestCase):

    @property
    def app_(self):
        class SubSubController(object):
            @expose()
            def index(self):
                return '/sub/sub/'

            @expose()
            def deeper(self):
                return '/sub/sub/deeper'

        class SubController(object):
            @expose()
            def index(self):
                return '/sub/'

            @expose()
            def deeper(self):
                return '/sub/deeper'

            sub = SubSubController()

        class RootController(object):
            @expose()
            def index(self):
                return '/'

            @expose()
            def deeper(self):
                return '/deeper'

            sub = SubController()

        return TestApp(Pecan(RootController()))

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
            def index(self):
                return '/%s' % self.someID

            @expose()
            def name(self):
                return '/%s/name' % self.someID

        class RootController(object):
            @expose()
            def index(self):
                return '/'

            @expose()
            def _lookup(self, someID, *remainder):
                return LookupController(someID), remainder

        return TestApp(Pecan(RootController()))

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
            app = TestApp(Pecan(RootController()))
            r = app.get('/foo/bar', expect_errors=True)
            assert r.status_int == 404


class TestCanonicalLookups(PecanTestCase):

    @property
    def app_(self):
        class LookupController(object):
            def __init__(self, someID):
                self.someID = someID

            @expose()
            def index(self):
                return self.someID

        class UserController(object):
            @expose()
            def _lookup(self, someID, *remainder):
                return LookupController(someID), remainder

        class RootController(object):
            users = UserController()

        return TestApp(Pecan(RootController()))

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
            def index(self, id):
                return 'index: %s' % id

            @expose()
            def multiple(self, one, two):
                return 'multiple: %s, %s' % (one, two)

            @expose()
            def optional(self, id=None):
                return 'optional: %s' % str(id)

            @expose()
            def multiple_optional(self, one=None, two=None, three=None):
                return 'multiple_optional: %s, %s, %s' % (one, two, three)

            @expose()
            def variable_args(self, *args):
                return 'variable_args: %s' % ', '.join(args)

            @expose()
            def variable_kwargs(self, **kwargs):
                data = [
                    '%s=%s' % (key, kwargs[key])
                    for key in sorted(kwargs.keys())
                ]
                return 'variable_kwargs: %s' % ', '.join(data)

            @expose()
            def variable_all(self, *args, **kwargs):
                data = [
                    '%s=%s' % (key, kwargs[key])
                    for key in sorted(kwargs.keys())
                ]
                return 'variable_all: %s' % ', '.join(list(args) + data)

            @expose()
            def eater(self, id, dummy=None, *args, **kwargs):
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

        return TestApp(Pecan(RootController()))

    def test_required_argument(self):
        try:
            r = self.app_.get('/')
            assert r.status_int != 200  # pragma: nocover
        except Exception as ex:
            assert type(ex) == TypeError
            assert ex.args[0] in (
                "index() takes exactly 2 arguments (1 given)",
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

    def test_explicit_json_kwargs(self):
        r = self.app_.post_json('/', {'id': '4'})
        assert r.status_int == 200
        assert r.body == b_('index: 4')

    def test_path_with_explicit_json_kwargs(self):
        r = self.app_.post_json('/4', {'id': 'four'})
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

    def test_json_kwargs_from_root(self):
        r = self.app_.post_json('/', {'id': '6', 'dummy': 'dummy'})
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

    def test_positional_args_with_json_kwargs(self):
        r = self.app_.post_json('/multiple', {'one': 'five', 'two': 'six'})
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

    def test_optional_arg_with_json_kwargs(self):
        r = self.app_.post_json('/optional', {'id': '4'})
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

    def test_multiple_positional_arguments_with_json_kwargs(self):
        r = self.app_.post_json('/optional/5', {'id': 'five'})
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

    def test_optional_arg_with_multiple_json_kwargs(self):
        r = self.app_.post_json('/optional', {'id': '7', 'dummy': 'dummy'})
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

    def test_multiple_optional_positional_args_with_json_kwargs(self):
        r = self.app_.post_json('/multiple_optional', {'one': '1'})
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

    def test_multiple_optional_positional_args_and_json_kwargs(self):
        r = self.app_.post_json('/multiple_optional/1', {'one': 'one'})
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

    def test_multiple_optional_args_with_multiple_json_kwargs(self):
        r = self.app_.post_json(
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

    def test_variable_args_with_json_kwargs(self):
        r = self.app_.post_json(
            '/variable_args',
            {'id': '3', 'dummy': 'dummy'}
        )
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

    def test_multiple_variable_kwargs_with_json_kwargs(self):
        r = self.app_.post_json(
            '/variable_kwargs',
            {'id': '3', 'dummy': 'dummy'}
        )
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

    def test_variable_post_with_json_kwargs(self):
        r = self.app_.post_json(
            '/variable_all/6',
            {'month': '1', 'day': '12'}
        )
        assert r.status_int == 200
        assert r.body == b_('variable_all: 6, day=12, month=1')

    def test_variable_post_mixed(self):
        r = self.app_.post(
            '/variable_all/7',
            {'id': 'seven', 'month': '1', 'day': '12'}
        )
        assert r.status_int == 200
        assert r.body == b_('variable_all: 7, day=12, id=seven, month=1')

    def test_variable_post_mixed_with_json(self):
        r = self.app_.post_json(
            '/variable_all/7',
            {'id': 'seven', 'month': '1', 'day': '12'}
        )
        assert r.status_int == 200
        assert r.body == b_('variable_all: 7, day=12, id=seven, month=1')

    def test_duplicate_query_parameters_GET(self):
        r = self.app_.get('/variable_kwargs?list=1&list=2')
        l = [u_('1'), u_('2')]
        assert r.status_int == 200
        assert r.body == b_('variable_kwargs: list=%s' % l)

    def test_duplicate_query_parameters_POST(self):
        r = self.app_.post('/variable_kwargs',
                           {'list': ['1', '2']})
        l = [u_('1'), u_('2')]
        assert r.status_int == 200
        assert r.body == b_('variable_kwargs: list=%s' % l)

    def test_duplicate_query_parameters_POST_mixed(self):
        r = self.app_.post('/variable_kwargs?list=1&list=2',
                           {'list': ['3', '4']})
        l = [u_('1'), u_('2'), u_('3'), u_('4')]
        assert r.status_int == 200
        assert r.body == b_('variable_kwargs: list=%s' % l)

    def test_duplicate_query_parameters_POST_mixed_json(self):
        r = self.app_.post('/variable_kwargs?list=1&list=2',
                           {'list': 3})
        l = [u_('1'), u_('2'), u_('3')]
        assert r.status_int == 200
        assert r.body == b_('variable_kwargs: list=%s' % l)

    def test_no_remainder(self):
        try:
            r = self.app_.get('/eater')
            assert r.status_int != 200  # pragma: nocover
        except Exception as ex:
            assert type(ex) == TypeError
            assert ex.args[0] in (
                "eater() takes at least 2 arguments (1 given)",
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

    def test_post_empty_remainder_with_json_kwargs(self):
        r = self.app_.post_json('/eater/9/', {'month': '1', 'day': '12'})
        assert r.status_int == 200
        assert r.body == b_('eater: 9, None, day=12, month=1')

    def test_post_remainder_with_json_kwargs(self):
        r = self.app_.post_json('/eater/9', {'month': '1', 'day': '12'})
        assert r.status_int == 200
        assert r.body == b_('eater: 9, None, day=12, month=1')

    def test_post_many_remainders_with_many_kwargs(self):
        r = self.app_.post(
            '/eater/10',
            {'id': 'ten', 'month': '1', 'day': '12', 'dummy': 'dummy'}
        )
        assert r.status_int == 200
        assert r.body == b_('eater: 10, dummy, day=12, month=1')

    def test_post_many_remainders_with_many_json_kwargs(self):
        r = self.app_.post_json(
            '/eater/10',
            {'id': 'ten', 'month': '1', 'day': '12', 'dummy': 'dummy'}
        )
        assert r.status_int == 200
        assert r.body == b_('eater: 10, dummy, day=12, month=1')


class TestDefaultErrorRendering(PecanTestCase):

    def test_plain_error(self):
        class RootController(object):
            pass

        app = TestApp(Pecan(RootController()))
        r = app.get('/', status=404)
        assert r.status_int == 404
        assert r.content_type == 'text/plain'
        assert r.body == b_(HTTPNotFound().plain_body({}))

    def test_html_error(self):
        class RootController(object):
            pass

        app = TestApp(Pecan(RootController()))
        r = app.get('/', headers={'Accept': 'text/html'}, status=404)
        assert r.status_int == 404
        assert r.content_type == 'text/html'
        assert r.body == b_(HTTPNotFound().html_body({}))

    def test_json_error(self):
        class RootController(object):
            pass

        app = TestApp(Pecan(RootController()))
        r = app.get('/', headers={'Accept': 'application/json'}, status=404)
        assert r.status_int == 404
        json_resp = json.loads(r.body.decode())
        assert json_resp['code'] == 404
        assert json_resp['description'] is None
        assert json_resp['title'] == 'Not Found'
        assert r.content_type == 'application/json'


class TestAbort(PecanTestCase):

    def test_abort(self):
        class RootController(object):
            @expose()
            def index(self):
                abort(404)

        app = TestApp(Pecan(RootController()))
        r = app.get('/', status=404)
        assert r.status_int == 404

    def test_abort_with_detail(self):
        class RootController(object):
            @expose()
            def index(self):
                abort(status_code=401, detail='Not Authorized')

        app = TestApp(Pecan(RootController()))
        r = app.get('/', status=401)
        assert r.status_int == 401


class TestScriptName(PecanTestCase):

    def setUp(self):
        super(TestScriptName, self).setUp()
        self.environ = {'SCRIPT_NAME': '/foo'}

    def test_handle_script_name(self):
        class RootController(object):
            @expose()
            def index(self):
                return 'Root Index'

        app = TestApp(Pecan(RootController()), extra_environ=self.environ)
        r = app.get('/foo/')
        assert r.status_int == 200


class TestRedirect(PecanTestCase):

    @property
    def app_(self):
        class RootController(object):
            @expose()
            def index(self):
                redirect('/testing')

            @expose()
            def internal(self):
                redirect('/testing', internal=True)

            @expose()
            def bad_internal(self):
                redirect('/testing', internal=True, code=301)

            @expose()
            def permanent(self):
                redirect('/testing', code=301)

            @expose()
            def testing(self):
                return 'it worked!'

        return TestApp(make_app(RootController(), debug=False))

    def test_index(self):
        r = self.app_.get('/')
        assert r.status_int == 302
        r = r.follow()
        assert r.status_int == 200
        assert r.body == b_('it worked!')

    def test_internal(self):
        r = self.app_.get('/internal')
        assert r.status_int == 200
        assert r.body == b_('it worked!')

    def test_internal_with_301(self):
        self.assertRaises(ValueError, self.app_.get, '/bad_internal')

    def test_permanent_redirect(self):
        r = self.app_.get('/permanent')
        assert r.status_int == 301
        r = r.follow()
        assert r.status_int == 200
        assert r.body == b_('it worked!')

    def test_x_forward_proto(self):
        class ChildController(object):
            @expose()
            def index(self):
                redirect('/testing')  # pragma: nocover

        class RootController(object):
            @expose()
            def index(self):
                redirect('/testing')  # pragma: nocover

            @expose()
            def testing(self):
                return 'it worked!'  # pragma: nocover
            child = ChildController()

        app = TestApp(make_app(RootController(), debug=True))
        res = app.get(
            '/child', extra_environ=dict(HTTP_X_FORWARDED_PROTO='https')
        )
        # non-canonical url will redirect, so we won't get a 301
        assert res.status_int == 302
        # should add trailing / and changes location to https
        assert res.location == 'https://localhost/child/'
        assert res.request.environ['HTTP_X_FORWARDED_PROTO'] == 'https'


class TestInternalRedirectContext(PecanTestCase):

    @property
    def app_(self):
        class RootController(object):

            @expose()
            def redirect_with_context(self):
                request.context['foo'] = 'bar'
                redirect('/testing')

            @expose()
            def internal_with_context(self):
                request.context['foo'] = 'bar'
                redirect('/testing', internal=True)

            @expose('json')
            def testing(self):
                return request.context

        return TestApp(make_app(RootController(), debug=False))

    def test_internal_with_request_context(self):
        r = self.app_.get('/internal_with_context')
        assert r.status_int == 200
        assert json.loads(r.body.decode()) == {'foo': 'bar'}

    def test_context_does_not_bleed(self):
        r = self.app_.get('/redirect_with_context').follow()
        assert r.status_int == 200
        assert json.loads(r.body.decode()) == {}


class TestStreamedResponse(PecanTestCase):

    def test_streaming_response(self):

        class RootController(object):
            @expose(content_type='text/plain')
            def test(self, foo):
                if foo == 'stream':
                    # mimic large file
                    contents = six.BytesIO(b_('stream'))
                    response.content_type = 'application/octet-stream'
                    contents.seek(0, os.SEEK_END)
                    response.content_length = contents.tell()
                    contents.seek(0, os.SEEK_SET)
                    response.app_iter = contents
                    return response
                else:
                    return 'plain text'

        app = TestApp(Pecan(RootController()))
        r = app.get('/test/stream')
        assert r.content_type == 'application/octet-stream'
        assert r.body == b_('stream')

        r = app.get('/test/plain')
        assert r.content_type == 'text/plain'
        assert r.body == b_('plain text')


class TestManualResponse(PecanTestCase):

    def test_manual_response(self):

        class RootController(object):
            @expose()
            def index(self):
                resp = webob.Response(response.environ)
                resp.body = b_('Hello, World!')
                return resp

        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.body == b_('Hello, World!')


class TestCustomResponseandRequest(PecanTestCase):

    def test_custom_objects(self):

        class CustomRequest(Request):

            @property
            def headers(self):
                headers = super(CustomRequest, self).headers
                headers['X-Custom-Request'] = 'ABC'
                return headers

        class CustomResponse(Response):

            @property
            def headers(self):
                headers = super(CustomResponse, self).headers
                headers['X-Custom-Response'] = 'XYZ'
                return headers

        class RootController(object):
            @expose()
            def index(self):
                return request.headers.get('X-Custom-Request')

        app = TestApp(Pecan(
            RootController(),
            request_cls=CustomRequest,
            response_cls=CustomResponse
        ))
        r = app.get('/')
        assert r.body == b_('ABC')
        assert r.headers.get('X-Custom-Response') == 'XYZ'


class TestThreadLocalState(PecanTestCase):

    def test_thread_local_dir(self):
        """
        Threadlocal proxies for request and response should properly
        proxy ``dir()`` calls to the underlying webob class.
        """
        class RootController(object):
            @expose()
            def index(self):
                assert 'method' in dir(request)
                assert 'status' in dir(response)
                return '/'

        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        assert r.body == b_('/')

    def test_request_state_cleanup(self):
        """
        After a request, the state local() should be totally clean
        except for state.app (so that objects don't leak between requests)
        """
        from pecan.core import state

        class RootController(object):
            @expose()
            def index(self):
                return '/'

        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        assert r.body == b_('/')

        assert state.__dict__ == {}


class TestFileTypeExtensions(PecanTestCase):

    @property
    def app_(self):
        """
        Test extension splits
        """
        class RootController(object):
            @expose(content_type=None)
            def _default(self, *args):
                ext = request.pecan['extension']
                assert len(args) == 1
                if ext:
                    assert ext not in args[0]
                return ext or ''

        return TestApp(Pecan(RootController()))

    def test_html_extension(self):
        r = self.app_.get('/index.html')
        assert r.status_int == 200
        assert r.body == b_('.html')

    def test_image_extension(self):
        r = self.app_.get('/image.png')
        assert r.status_int == 200
        assert r.body == b_('.png')

    def test_hidden_file(self):
        r = self.app_.get('/.vimrc')
        assert r.status_int == 204
        assert r.body == b_('')

    def test_multi_dot_extension(self):
        r = self.app_.get('/gradient.min.js')
        assert r.status_int == 200
        assert r.body == b_('.js')

    def test_bad_content_type(self):
        class RootController(object):
            @expose()
            def index(self):
                return '/'

        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        assert r.body == b_('/')

        r = app.get('/index.html', expect_errors=True)
        assert r.status_int == 200
        assert r.body == b_('/')

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = app.get('/index.txt', expect_errors=True)
            assert r.status_int == 404

    def test_unknown_file_extension(self):
        class RootController(object):
            @expose(content_type=None)
            def _default(self, *args):
                assert 'example:x.tiny' in args
                assert request.pecan['extension'] is None
                return 'SOME VALUE'

        app = TestApp(Pecan(RootController()))

        r = app.get('/example:x.tiny')
        assert r.status_int == 200
        assert r.body == b_('SOME VALUE')

    def test_guessing_disabled(self):
        class RootController(object):
            @expose(content_type=None)
            def _default(self, *args):
                assert 'index.html' in args
                assert request.pecan['extension'] is None
                return 'SOME VALUE'

        app = TestApp(Pecan(RootController(),
                            guess_content_type_from_ext=False))

        r = app.get('/index.html')
        assert r.status_int == 200
        assert r.body == b_('SOME VALUE')


class TestContentTypeByAcceptHeaders(PecanTestCase):

    @property
    def app_(self):
        """
        Test that content type is set appropriately based on Accept headers.
        """
        class RootController(object):

            @expose(content_type='text/html')
            @expose(content_type='application/json')
            def index(self, *args):
                return 'Foo'

        return TestApp(Pecan(RootController()))

    def test_quality(self):
        r = self.app_.get('/', headers={
            'Accept': 'text/html,application/json;q=0.9,*/*;q=0.8'
        })
        assert r.status_int == 200
        assert r.content_type == 'text/html'

        r = self.app_.get('/', headers={
            'Accept': 'application/json,text/html;q=0.9,*/*;q=0.8'
        })
        assert r.status_int == 200
        assert r.content_type == 'application/json'

    def test_file_extension_has_higher_precedence(self):
        r = self.app_.get('/index.html', headers={
            'Accept': 'application/json,text/html;q=0.9,*/*;q=0.8'
        })
        assert r.status_int == 200
        assert r.content_type == 'text/html'

    def test_not_acceptable(self):
        r = self.app_.get('/', headers={
            'Accept': 'application/xml',
        }, status=406)
        assert r.status_int == 406

    def test_accept_header_missing(self):
        r = self.app_.get('/')
        assert r.status_int == 200
        assert r.content_type == 'text/html'


class TestCanonicalRouting(PecanTestCase):

    @property
    def app_(self):
        class ArgSubController(object):
            @expose()
            def index(self, arg):
                return arg

        class AcceptController(object):
            @accept_noncanonical
            @expose()
            def index(self):
                return 'accept'

        class SubController(object):
            @expose()
            def index(self, **kw):
                return 'subindex'

        class RootController(object):
            @expose()
            def index(self):
                return 'index'

            sub = SubController()
            arg = ArgSubController()
            accept = AcceptController()

        return TestApp(Pecan(RootController()))

    def test_root(self):
        r = self.app_.get('/')
        assert r.status_int == 200
        assert b_('index') in r.body

    def test_index(self):
        r = self.app_.get('/index')
        assert r.status_int == 200
        assert b_('index') in r.body

    def test_broken_clients(self):
        # for broken clients
        r = self.app_.get('', status=302)
        assert r.status_int == 302
        assert r.location == 'http://localhost/'

    def test_sub_controller_with_trailing(self):
        r = self.app_.get('/sub/')
        assert r.status_int == 200
        assert b_('subindex') in r.body

    def test_sub_controller_redirect(self):
        r = self.app_.get('/sub', status=302)
        assert r.status_int == 302
        assert r.location == 'http://localhost/sub/'

    def test_with_query_string(self):
        # try with query string
        r = self.app_.get('/sub?foo=bar', status=302)
        assert r.status_int == 302
        assert r.location == 'http://localhost/sub/?foo=bar'

    def test_posts_fail(self):
        try:
            self.app_.post('/sub', dict(foo=1))
            raise Exception("Post should fail")  # pragma: nocover
        except Exception as e:
            assert isinstance(e, RuntimeError)

    def test_with_args(self):
        r = self.app_.get('/arg/index/foo')
        assert r.status_int == 200
        assert r.body == b_('foo')

    def test_accept_noncanonical(self):
        r = self.app_.get('/accept/')
        assert r.status_int == 200
        assert r.body == b_('accept')

    def test_accept_noncanonical_no_trailing_slash(self):
        r = self.app_.get('/accept')
        assert r.status_int == 200
        assert r.body == b_('accept')


class TestNonCanonical(PecanTestCase):

    @property
    def app_(self):
        class ArgSubController(object):
            @expose()
            def index(self, arg):
                return arg  # pragma: nocover

        class AcceptController(object):
            @accept_noncanonical
            @expose()
            def index(self):
                return 'accept'  # pragma: nocover

        class SubController(object):
            @expose()
            def index(self, **kw):
                return 'subindex'

        class RootController(object):
            @expose()
            def index(self):
                return 'index'

            sub = SubController()
            arg = ArgSubController()
            accept = AcceptController()

        return TestApp(Pecan(RootController(), force_canonical=False))

    def test_index(self):
        r = self.app_.get('/')
        assert r.status_int == 200
        assert b_('index') in r.body

    def test_subcontroller(self):
        r = self.app_.get('/sub')
        assert r.status_int == 200
        assert b_('subindex') in r.body

    def test_subcontroller_with_kwargs(self):
        r = self.app_.post('/sub', dict(foo=1))
        assert r.status_int == 200
        assert b_('subindex') in r.body

    def test_sub_controller_with_trailing(self):
        r = self.app_.get('/sub/')
        assert r.status_int == 200
        assert b_('subindex') in r.body

    def test_proxy(self):
        class RootController(object):
            @expose()
            def index(self):
                request.testing = True
                assert request.testing is True
                del request.testing
                assert hasattr(request, 'testing') is False
                return '/'

        app = TestApp(make_app(RootController(), debug=True))
        r = app.get('/')
        assert r.status_int == 200

    def test_app_wrap(self):
        class RootController(object):
            pass

        wrapped_apps = []

        def wrap(app):
            wrapped_apps.append(app)
            return app

        make_app(RootController(), wrap_app=wrap, debug=True)
        assert len(wrapped_apps) == 1


class TestLogging(PecanTestCase):

    def test_logging_setup(self):
        class RootController(object):
            @expose()
            def index(self):
                import logging
                logging.getLogger('pecantesting').info('HELLO WORLD')
                return "HELLO WORLD"

        f = StringIO()

        app = TestApp(make_app(RootController(), logging={
            'loggers': {
                'pecantesting': {
                    'level': 'INFO', 'handlers': ['memory']
                }
            },
            'handlers': {
                'memory': {
                    'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'stream': f
                }
            }
        }))

        app.get('/')
        assert f.getvalue() == 'HELLO WORLD\n'

    def test_logging_setup_with_config_obj(self):
        class RootController(object):
            @expose()
            def index(self):
                import logging
                logging.getLogger('pecantesting').info('HELLO WORLD')
                return "HELLO WORLD"

        f = StringIO()

        from pecan.configuration import conf_from_dict
        app = TestApp(make_app(RootController(), logging=conf_from_dict({
            'loggers': {
                'pecantesting': {
                    'level': 'INFO', 'handlers': ['memory']
                }
            },
            'handlers': {
                'memory': {
                    'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'stream': f
                }
            }
        })))

        app.get('/')
        assert f.getvalue() == 'HELLO WORLD\n'


class TestEngines(PecanTestCase):

    template_path = os.path.join(os.path.dirname(__file__), 'templates')

    @unittest.skipIf('genshi' not in builtin_renderers, 'Genshi not installed')
    def test_genshi(self):

        class RootController(object):
            @expose('genshi:genshi.html')
            def index(self, name='Jonathan'):
                return dict(name=name)

            @expose('genshi:genshi_bad.html')
            def badtemplate(self):
                return dict()

        app = TestApp(
            Pecan(RootController(), template_path=self.template_path)
        )
        r = app.get('/')
        assert r.status_int == 200
        assert b_("<h1>Hello, Jonathan!</h1>") in r.body

        r = app.get('/index.html?name=World')
        assert r.status_int == 200
        assert b_("<h1>Hello, World!</h1>") in r.body

        error_msg = None
        try:
            r = app.get('/badtemplate.html')
        except Exception as e:
            for error_f in error_formatters:
                error_msg = error_f(e)
                if error_msg:
                    break
        assert error_msg is not None

    @unittest.skipIf('kajiki' not in builtin_renderers, 'Kajiki not installed')
    def test_kajiki(self):

        class RootController(object):
            @expose('kajiki:kajiki.html')
            def index(self, name='Jonathan'):
                return dict(name=name)

        app = TestApp(
            Pecan(RootController(), template_path=self.template_path)
        )
        r = app.get('/')
        assert r.status_int == 200
        assert b_("<h1>Hello, Jonathan!</h1>") in r.body

        r = app.get('/index.html?name=World')
        assert r.status_int == 200
        assert b_("<h1>Hello, World!</h1>") in r.body

    @unittest.skipIf('jinja' not in builtin_renderers, 'Jinja not installed')
    def test_jinja(self):

        class RootController(object):
            @expose('jinja:jinja.html')
            def index(self, name='Jonathan'):
                return dict(name=name)

            @expose('jinja:jinja_bad.html')
            def badtemplate(self):
                return dict()

        app = TestApp(
            Pecan(RootController(), template_path=self.template_path)
        )
        r = app.get('/')
        assert r.status_int == 200
        assert b_("<h1>Hello, Jonathan!</h1>") in r.body

        error_msg = None
        try:
            r = app.get('/badtemplate.html')
        except Exception as e:
            for error_f in error_formatters:
                error_msg = error_f(e)
                if error_msg:
                    break
        assert error_msg is not None

    @unittest.skipIf('mako' not in builtin_renderers, 'Mako not installed')
    def test_mako(self):

        class RootController(object):
            @expose('mako:mako.html')
            def index(self, name='Jonathan'):
                return dict(name=name)

            @expose('mako:mako_bad.html')
            def badtemplate(self):
                return dict()

        app = TestApp(
            Pecan(RootController(), template_path=self.template_path)
        )
        r = app.get('/')
        assert r.status_int == 200
        assert b_("<h1>Hello, Jonathan!</h1>") in r.body

        r = app.get('/index.html?name=World')
        assert r.status_int == 200
        assert b_("<h1>Hello, World!</h1>") in r.body

        error_msg = None
        try:
            r = app.get('/badtemplate.html')
        except Exception as e:
            for error_f in error_formatters:
                error_msg = error_f(e)
                if error_msg:
                    break
        assert error_msg is not None

    def test_json(self):
        try:
            from simplejson import loads
        except:
            from json import loads  # noqa

        expected_result = dict(
            name='Jonathan',
            age=30, nested=dict(works=True)
        )

        class RootController(object):
            @expose('json')
            def index(self):
                return expected_result

        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        result = dict(loads(r.body.decode()))
        assert result == expected_result

    def test_override_template(self):
        class RootController(object):
            @expose('foo.html')
            def index(self):
                override_template(None, content_type='text/plain')
                return 'Override'

        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        assert b_('Override') in r.body
        assert r.content_type == 'text/plain'

    def test_render(self):
        class RootController(object):
            @expose()
            def index(self, name='Jonathan'):
                return render('mako.html', dict(name=name))

        app = TestApp(
            Pecan(RootController(), template_path=self.template_path)
        )
        r = app.get('/')
        assert r.status_int == 200
        assert b_("<h1>Hello, Jonathan!</h1>") in r.body

    def test_default_json_renderer(self):

        class RootController(object):
            @expose()
            def index(self, name='Bill'):
                return dict(name=name)

        app = TestApp(Pecan(RootController(), default_renderer='json'))
        r = app.get('/')
        assert r.status_int == 200
        result = dict(json.loads(r.body.decode()))
        assert result == {'name': 'Bill'}


class TestDeprecatedRouteMethod(PecanTestCase):

    @property
    def app_(self):
        class RootController(object):

            @expose()
            def index(self, *args):
                return ', '.join(args)

            @expose()
            def _route(self, args):
                return self.index, args

        return TestApp(Pecan(RootController()))

    def test_required_argument(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = self.app_.get('/foo/bar/')
            assert r.status_int == 200
            assert b_('foo, bar') in r.body
