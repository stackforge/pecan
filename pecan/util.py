import sys
import os


def iscontroller(obj):
    return getattr(obj, 'exposed', False)


def _cfg(f):
    if not hasattr(f, '_pecan'):
        f._pecan = {}
    return f._pecan


def compat_splitext(path):
    """
    This method emulates the behavior os.path.splitext introduced in python 2.6
    """
    basename = os.path.basename(path)

    index = basename.rfind('.')
    if index > 0:
        root = basename[:index]
        if root.count('.') != index:
            return (
                os.path.join(os.path.dirname(path), root),
                basename[index:]
            )

    return (path, '')


# use the builtin splitext unless we're python 2.5
if sys.version_info >= (2, 6):
    from os.path import splitext
else:                             # pragma no cover
    splitext = compat_splitext    # noqa


if sys.version_info >= (2, 6, 5):
    def encode_if_needed(s):
        return s
else:
    def encode_if_needed(s):  # noqa
        return s.encode('utf-8')
