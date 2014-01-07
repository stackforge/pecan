import sys


def iscontroller(obj):
    return getattr(obj, 'exposed', False)


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
