import inspect
import sys

import six


def iscontroller(obj):
    return getattr(obj, 'exposed', False)


def getargspec(method):
    """
    Drill through layers of decorators attempting to locate the actual argspec
    for a method.
    """

    argspec = inspect.getargspec(method)
    args = argspec[0]
    if args and args[0] == 'self':
        return argspec
    if hasattr(method, '__func__'):
        method = method.__func__

    func_closure = six.get_function_closure(method)

    # NOTE(sileht): if the closure is None we cannot look deeper,
    # so return actual argspec, this occurs when the method
    # is static for example.
    if func_closure is None:
        return argspec

    closure = next(
        (
            c for c in func_closure if six.callable(c.cell_contents)
        ),
        None
    )
    method = closure.cell_contents
    return getargspec(method)


def _cfg(f):
    if not hasattr(f, '_pecan'):
        f._pecan = {}
    return f._pecan


if sys.version_info >= (2, 6, 5):
    def encode_if_needed(s):
        return s
else:
    def encode_if_needed(s):  # noqa
        return s.encode('utf-8')
