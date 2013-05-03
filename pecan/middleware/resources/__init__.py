import os
from mimetypes import guess_type
from contextlib import closing
from base64 import b64encode

import six

from pecan.compat import quote


def load_resource(filename):
    with closing(open(
        os.path.join(
            os.path.dirname(__file__),
            filename
        ),
        'rb'
    )) as f:
        data = f.read()
        if six.PY3:
            data = data.replace(b'\n', b'')  # pragma: nocover
        else:
            data.replace('\n', '')
        return 'data:%s;base64,%s' % (
            guess_type(filename)[0],
            quote(b64encode(data))
        )

pecan_image = load_resource('pecan.png')
xregexp_js = load_resource('XRegExp.js')
syntax_js = load_resource('shCore.js')
syntax_css = load_resource('syntax.css')
theme = load_resource('theme.css')
brush = load_resource('brush-python.js')
