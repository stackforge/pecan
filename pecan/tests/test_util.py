import functools
import inspect
import unittest

from pecan import expose
from pecan import util


class TestArgSpec(unittest.TestCase):

    @property
    def controller(self):

        class RootController(object):

            @expose()
            def index(self, a, b, c=1, *args, **kwargs):
                return 'Hello, World!'

            @staticmethod
            @expose()
            def static_index(a, b, c=1, *args, **kwargs):
                return 'Hello, World!'

        return RootController()

    def test_no_decorator(self):
        expected = inspect.getargspec(self.controller.index.__func__)
        actual = util.getargspec(self.controller.index.__func__)
        assert expected == actual

        expected = inspect.getargspec(self.controller.static_index)
        actual = util.getargspec(self.controller.static_index)
        assert expected == actual

    def test_simple_decorator(self):
        def dec(f):
            return f

        expected = inspect.getargspec(self.controller.index.__func__)
        actual = util.getargspec(dec(self.controller.index.__func__))
        assert expected == actual

        expected = inspect.getargspec(self.controller.static_index)
        actual = util.getargspec(dec(self.controller.static_index))
        assert expected == actual

    def test_simple_wrapper(self):
        def dec(f):
            @functools.wraps(f)
            def wrapped(*a, **kw):
                return f(*a, **kw)
            return wrapped

        expected = inspect.getargspec(self.controller.index.__func__)
        actual = util.getargspec(dec(self.controller.index.__func__))
        assert expected == actual

        expected = inspect.getargspec(self.controller.static_index)
        actual = util.getargspec(dec(self.controller.static_index))
        assert expected == actual

    def test_multiple_decorators(self):
        def dec(f):
            @functools.wraps(f)
            def wrapped(*a, **kw):
                return f(*a, **kw)
            return wrapped

        expected = inspect.getargspec(self.controller.index.__func__)
        actual = util.getargspec(dec(dec(dec(self.controller.index.__func__))))
        assert expected == actual

        expected = inspect.getargspec(self.controller.static_index)
        actual = util.getargspec(dec(dec(dec(
            self.controller.static_index))))
        assert expected == actual

    def test_decorator_with_args(self):
        def dec(flag):
            def inner(f):
                @functools.wraps(f)
                def wrapped(*a, **kw):
                    return f(*a, **kw)
                return wrapped
            return inner

        expected = inspect.getargspec(self.controller.index.__func__)
        actual = util.getargspec(dec(True)(self.controller.index.__func__))
        assert expected == actual

        expected = inspect.getargspec(self.controller.static_index)
        actual = util.getargspec(dec(True)(
            self.controller.static_index))
        assert expected == actual
