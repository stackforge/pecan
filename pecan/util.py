import sys


def memodict(f):
    """ Memoization decorator for a function taking a single argument """
    class memodict(dict):
        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret
    return memodict().__getitem__


@memodict
def iscontroller(obj):
    return getattr(obj, 'exposed', False)


@memodict
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
