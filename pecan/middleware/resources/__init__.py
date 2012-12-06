import os
import urllib
from mimetypes import guess_type
from contextlib import closing


def load_resource(filename):
    with closing(open(
        os.path.join(
            os.path.dirname(__file__),
            filename
        ),
        'rb'
    )) as f:
        return 'data:%s;base64,%s' % (
            guess_type(filename)[0],
            urllib.quote(
                f.read().encode('base64').replace('\n', '')
            )
        )

pecan_image = load_resource('pecan.png')
syntax_js = load_resource('syntax.js')
syntax_css = load_resource('syntax.css')
theme = load_resource('theme.css')
brush = load_resource('brush-python.js')
