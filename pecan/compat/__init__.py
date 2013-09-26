import inspect

import six

if six.PY3:
    import urllib.parse as urlparse
    from urllib.parse import quote, unquote_plus
    from urllib.request import urlopen, URLError
    from html import escape
    izip = zip
else:
    import urlparse  # noqa
    from urllib import quote, unquote_plus  # noqa
    from urllib2 import urlopen, URLError  # noqa
    from cgi import escape  # noqa
    from itertools import izip


def is_bound_method(ob):
    return inspect.ismethod(ob) and six.get_method_self(ob) is not None
