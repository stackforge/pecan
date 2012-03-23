from cStringIO import StringIO
from traceback import print_exc
from pprint import pformat

from mako.template import Template

from webob import Response

import pdb

debug_template_raw = '''<html>
 <head>
  <title>Pecan - Application Error</title>

  <link rel="stylesheet" type="text/css" href="${shcorecss}" />
  <link rel="stylesheet" type="text/css" href="${shthemedefault}" />

  <script type="text/javascript" src="${shcore}">
    /**
     * SyntaxHighlighter
     * http://alexgorbatchev.com/SyntaxHighlighter
     *
     * SyntaxHighlighter is donationware. If you are using it, please donate.
     * http://alexgorbatchev.com/SyntaxHighlighter/donate.html
     *
     * @version
     * 3.0.83 (July 02 2010)
     *
     * @copyright
     * Copyright (C) 2004-2010 Alex Gorbatchev.
     *
     * @license
     * Dual licensed under the MIT and GPL licenses.
     */
  </script>
  <script type="text/javascript" src="${shbrushpython}">
    /**
     * SyntaxHighlighter
     * http://alexgorbatchev.com/SyntaxHighlighter
     *
     * SyntaxHighlighter is donationware. If you are using it, please donate.
     * http://alexgorbatchev.com/SyntaxHighlighter/donate.html
     *
     * @version
     * 3.0.83 (July 02 2010)
     *
     * @copyright
     * Copyright (C) 2004-2010 Alex Gorbatchev.
     *
     * @license
     * Dual licensed under the MIT and GPL licenses.
     */
  </script>

  <style type="text/css">
    body {
      color: #000;
      background: #FFF;
      font-family: 'Helvetica Neue', 'Helvetica', 'Verdana', sans-serif;
      font-size: 12px;
      padding: 0;
      margin: 0;
    }

    a {
      color: #FAFF78;
    }

    h1, h2, h3, h4, h5, h6 {
      font-family: 'Helvetica', sans-serif;
    }

    h1 {
      margin: 0;
      padding: .75em 1.5em 1em 1.5em;
      color: #F90;
      font-size: 14px;
      font-weight: bold;
    }

    h1 img  {
      padding-right: 5px;
    }

    h2 {
      color: #311F00;
    }

    header  {
      width: 100%;
      background: #311F00;
    }

    div#error-content  {
      padding: 0 2em;
    }

    .syntaxhighlighter a,
    .syntaxhighlighter div,
    .syntaxhighlighter code,
    .syntaxhighlighter table,
    .syntaxhighlighter table td,
    .syntaxhighlighter table tr,
    .syntaxhighlighter table tbody,
    .syntaxhighlighter table thead,
    .syntaxhighlighter table caption,
    .syntaxhighlighter textarea {
      font-family: monospace !important;
    }

    .syntaxhighlighter .container {
       background: #FDF6E3 !important;
       padding: 1em !important;
    }

    .syntaxhighlighter .container .line {
       background: #FDF6E3 !important;
    }

    .syntaxhighlighter .container .line .python.string {
       color: #C70 !important;
    }

    #debug {
        background: #FDF6E3;
        padding: 10px !important;
        margin-top: 10px;
        font-family: monospace;
    }

  </style>
  <script type="text/javascript">
      SyntaxHighlighter.defaults['gutter'] = false;
      SyntaxHighlighter.defaults['toolbar'] = false;
      SyntaxHighlighter.all()
  </script>

  <script type="text/javascript">
    function get_request() {
        /* ajax sans jquery makes me sad */
        var request = false;

        // Mozilla/Safari
        if (window.XMLHttpRequest) {
            request = new XMLHttpRequest();
        }

        // IE
        else if (window.ActiveXObject) {
            request = new ActiveXObject("Microsoft.XMLHTTP");
        }

        return request;
    }

    function debug_request(btn) {
        btn.disabled = true;

        request = get_request();
        request.open('GET', '/__pecan_initiate_pdb__', true);
        request.onreadystatechange = function() {
            if (request.readyState == 4) {
                btn.disabled = false;
            }
        }
        request.send('');

        /* automatically timeout after 5 minutes, re-enabling the button */
        setTimeout(function() {
           request.abort();
        }, 5 * 60 * 1000);
    }
  </script>
 </head>
 <body>

  <header>
    <h1>
      <img style="padding-top: 7px"
           align="center" alt="pecan logo"
           height="25"
           src="${pecan_image}" />
      application error
    </h1>
  </header>

  <div id="error-content">

    <p>
      <b>To disable this interface, set </b>
      <pre class="brush: python">conf.app.debug = False</pre>
    </p>

    <h2>Traceback</h2>
    <div id="traceback">
      <pre class="brush: python">${traceback}</pre>
    </div>

    % if not debugging:
    <b>Want to debug this request?</b>
    <div id="debug">
      You can <button onclick="debug_request(this)">
        repeat this request
      </button> with a Python debugger breakpoint.
    </div>
    % endif

    <h2>WSGI Environment</h2>
    <div id="environ">
      <pre class="brush: python">${environment}</pre>
    </div>
  </div>
 </body>
</html>
'''

debug_template = Template(debug_template_raw)
__debug_environ__ = None


class PdbMiddleware(object):
    def __init__(self, app, debugger):
        self.app = app
        self.debugger = debugger

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except:
            self.debugger()


class DebugMiddleware(object):
    """A WSGI middleware that provides debugging assistance for development
    environments.

    To enable the debugging middleware, simply set the ``debug`` flag to
    ``True`` in your configuration file::

        app = {
            ...
            'debug': True,
            ...
        }

    Once enabled, the middleware will automatically catch exceptions raised by
    your application, and display the Python stack trace and WSGI environment
    in your browser for easy debugging.

    To further aid in debugging, the middleware includes the ability to repeat
    the offending request, automatically inserting a breakpoint, and dropping
    your console into the Python debugger, ``pdb``.

    For more information, refer to the  `documentation for pdb
    <http://docs.python.org/library/pdb.html>`_ available on the Python
    website.

    :param app: the application to wrap.
    :param debugger: a callable to start debugging, defaulting to the Python
                     debugger, ``pdb``.
    """

    def __init__(self, app, debugger=pdb.post_mortem):
        self.app = app
        self.debugger = debugger

    def __call__(self, environ, start_response):
        assert not environ['wsgi.multiprocess'], (
            "The DebugMiddleware middleware is not usable in a "
            "multi-process environment")

        # initiate a PDB session if requested
        global __debug_environ__
        debugging = environ['PATH_INFO'] == '/__pecan_initiate_pdb__'
        if debugging:
            PdbMiddleware(self.app, self.debugger)(
                __debug_environ__, start_response
            )
            environ = __debug_environ__

        try:
            return self.app(environ, start_response)
        except:
            # save the environ for debugging
            if not debugging:
                __debug_environ__ = environ

            # get a formatted exception
            out = StringIO()
            print_exc(file=out)

            # get formatted WSGI environment
            formatted_environ = pformat(environ)

            # render our template
            result = debug_template.render(
                traceback=out.getvalue(),
                environment=formatted_environ,
                pecan_image=pecan_image,
                shcore=shcore,
                shbrushpython=shbrushpython,
                shcorecss=shcorecss,
                shthemedefault=shthemedefault,
                debugging=debugging
            )

            # construct and return our response
            response = Response()
            response.status_int = 400
            response.unicode_body = result
            return response(environ, start_response)

pecan_image = ("data:image/png;base64,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%3D")

shcore = ("data:application/x-javascript;base64,LyoqCiAqIFN5bnRheEhpZ2hsaWdodG"
"VyCiAqIGh0dHA6Ly9hbGV4Z29yYmF0Y2hldi5jb20vU3ludGF4SGlnaGxpZ2h0ZXIKICoKICogU3l"
"udGF4SGlnaGxpZ2h0ZXIgaXMgZG9uYXRpb253YXJlLiBJZiB5b3UgYXJlIHVzaW5nIGl0LCBwbGVh"
"c2UgZG9uYXRlLgogKiBodHRwOi8vYWxleGdvcmJhdGNoZXYuY29tL1N5bnRheEhpZ2hsaWdodGVyL"
"2RvbmF0ZS5odG1sCiAqCiAqIEB2ZXJzaW9uCiAqIDMuMC44MyAoSnVseSAwMiAyMDEwKQogKiAKIC"
"ogQGNvcHlyaWdodAogKiBDb3B5cmlnaHQgKEMpIDIwMDQtMjAxMCBBbGV4IEdvcmJhdGNoZXYuCiA"
"qCiAqIEBsaWNlbnNlCiAqIER1YWwgbGljZW5zZWQgdW5kZXIgdGhlIE1JVCBhbmQgR1BMIGxpY2Vu"
"c2VzLgogKi8KZXZhbChmdW5jdGlvbihwLGEsYyxrLGUsZCl7ZT1mdW5jdGlvbihjKXtyZXR1cm4oY"
"zxhPycnOmUocGFyc2VJbnQoYy9hKSkpKygoYz1jJWEpPjM1P1N0cmluZy5mcm9tQ2hhckNvZGUoYy"
"syOSk6Yy50b1N0cmluZygzNikpfTtpZighJycucmVwbGFjZSgvXi8sU3RyaW5nKSl7d2hpbGUoYy0"
"tKXtkW2UoYyldPWtbY118fGUoYyl9az1bZnVuY3Rpb24oZSl7cmV0dXJuIGRbZV19XTtlPWZ1bmN0"
"aW9uKCl7cmV0dXJuJ1xcdysnfTtjPTF9O3doaWxlKGMtLSl7aWYoa1tjXSl7cD1wLnJlcGxhY2Uob"
"mV3IFJlZ0V4cCgnXFxiJytlKGMpKydcXGInLCdnJyksa1tjXSl9fXJldHVybiBwfSgnSyBNO0koTS"
"kxUyAyVSgiMmFcJ3QgNGsgTSA0SyAyZyAzbCA0RyA0SCIpOyg2KCl7NiByKGYsZSl7SSghTS4xUih"
"mKSkxUyAzbSgiM3MgMTUgNFIiKTtLIGE9Zi4xdztmPU0oZi4xbSx0KGYpKyhlfHwiIikpO0koYSlm"
"LjF3PXsxbTphLjFtLDE5OmEuMTk/YS4xOS4xYSgwKTpOfTtIIGZ9NiB0KGYpe0goZi4xSj8iZyI6I"
"iIpKyhmLjRzPyJpIjoiIikrKGYuNHA/Im0iOiIiKSsoZi40dj8ieCI6IiIpKyhmLjNuPyJ5IjoiIi"
"l9NiBCKGYsZSxhLGIpe0sgYz11LkwsZCxoLGc7dj1SOzVLe08oO2MtLTspe2c9dVtjXTtJKGEmZy4"
"zciYmKCFnLjJwfHxnLjJwLlcoYikpKXtnLjJxLjEyPWU7SSgoaD1nLjJxLlgoZikpJiZoLlA9PT1l"
"KXtkPXszazpnLjJiLlcoYixoLGEpLDFDOmh9OzFOfX19fTV2KGkpezFTIGl9NXF7dj0xMX1IIGR9N"
"iBwKGYsZSxhKXtJKDNiLlouMWkpSCBmLjFpKGUsYSk7TyhhPWF8fDA7YTxmLkw7YSsrKUkoZlthXT"
"09PWUpSCBhO0gtMX1NPTYoZixlKXtLIGE9W10sYj1NLjFCLGM9MCxkLGg7SShNLjFSKGYpKXtJKGU"
"hPT0xZCkxUyAzbSgiMmFcJ3QgNXIgNUkgNUYgNUIgNUMgMTUgNUUgNXAiKTtIIHIoZil9SSh2KTFT"
"IDJVKCIyYVwndCBXIDNsIE0gNTkgNW0gNWcgNXggNWkiKTtlPWV8fCIiO08oZD17Mk46MTEsMTk6W"
"10sMks6NihnKXtIIGUuMWkoZyk+LTF9LDNkOjYoZyl7ZSs9Z319O2M8Zi5MOylJKGg9QihmLGMsYi"
"xkKSl7YS5VKGguM2spO2MrPWguMUNbMF0uTHx8MX1ZIEkoaD1uLlguVyh6W2JdLGYuMWEoYykpKXt"
"hLlUoaFswXSk7Yys9aFswXS5MfVl7aD1mLjNhKGMpO0koaD09PSJbIiliPU0uMkk7WSBJKGg9PT0i"
"XSIpYj1NLjFCO2EuVShoKTtjKyt9YT0xNShhLjFLKCIiKSxuLlEuVyhlLHcsIiIpKTthLjF3PXsxb"
"TpmLDE5OmQuMk4/ZC4xOTpOfTtIIGF9O00uM3Y9IjEuNS4wIjtNLjJJPTE7TS4xQj0yO0sgQz0vXF"
"wkKD86KFxcZFxcZD98WyQmYFwnXSl8eyhbJFxcd10rKX0pL2csdz0vW141aF0rfChbXFxzXFxTXSk"
"oPz1bXFxzXFxTXSpcXDEpL2csQT0vXig/Ols/KitdfHtcXGQrKD86LFxcZCopP30pXFw/Py8sdj0x"
"MSx1PVtdLG49e1g6MTUuWi5YLDFBOjE1LlouMUEsMUM6MXIuWi4xQyxROjFyLlouUSwxZToxci5aL"
"jFlfSx4PW4uWC5XKC8oKT8/LywiIilbMV09PT0xZCxEPTYoKXtLIGY9L14vZztuLjFBLlcoZiwiIi"
"k7SCFmLjEyfSgpLHk9Nigpe0sgZj0veC9nO24uUS5XKCJ4IixmLCIiKTtIIWYuMTJ9KCksRT0xNS5"
"aLjNuIT09MWQsej17fTt6W00uMkldPS9eKD86XFxcXCg/OlswLTNdWzAtN117MCwyfXxbNC03XVsw"
"LTddP3x4W1xcMjktMjYtZl17Mn18dVtcXDI5LTI2LWZdezR9fGNbQS0zby16XXxbXFxzXFxTXSkpL"
"zt6W00uMUJdPS9eKD86XFxcXCg/OjAoPzpbMC0zXVswLTddezAsMn18WzQtN11bMC03XT8pP3xbMS"
"05XVxcZCp8eFtcXDI5LTI2LWZdezJ9fHVbXFwyOS0yNi1mXXs0fXxjW0EtM28tel18W1xcc1xcU10"
"pfFxcKFxcP1s6PSFdfFs/KitdXFw/fHtcXGQrKD86LFxcZCopP31cXD8/KS87TS4xaD02KGYsZSxh"
"LGIpe3UuVSh7MnE6cihmLCJnIisoRT8ieSI6IiIpKSwyYjplLDNyOmF8fE0uMUIsMnA6Ynx8Tn0pf"
"TtNLjJuPTYoZixlKXtLIGE9ZisiLyIrKGV8fCIiKTtIIE0uMm5bYV18fChNLjJuW2FdPU0oZixlKS"
"l9O00uM2M9NihmKXtIIHIoZiwiZyIpfTtNLjVsPTYoZil7SCBmLlEoL1stW1xcXXt9KCkqKz8uLFx"
"cXFxeJHwjXFxzXS9nLCJcXFxcJCYiKX07TS41ZT02KGYsZSxhLGIpe2U9cihlLCJnIisoYiYmRT8i"
"eSI6IiIpKTtlLjEyPWE9YXx8MDtmPWUuWChmKTtIIGI/ZiYmZi5QPT09YT9mOk46Zn07TS4zcT02K"
"Cl7TS4xaD02KCl7MVMgMlUoIjJhXCd0IDU1IDFoIDU0IDNxIil9fTtNLjFSPTYoZil7SCA1My5aLj"
"FxLlcoZik9PT0iWzJtIDE1XSJ9O00uM3A9NihmLGUsYSxiKXtPKEsgYz1yKGUsImciKSxkPS0xLGg"
"7aD1jLlgoZik7KXthLlcoYixoLCsrZCxmLGMpO2MuMTI9PT1oLlAmJmMuMTIrK31JKGUuMUopZS4x"
"Mj0wfTtNLjU3PTYoZixlKXtIIDYgYShiLGMpe0sgZD1lW2NdLjFJP2VbY106ezFJOmVbY119LGg9c"
"ihkLjFJLCJnIiksZz1bXSxpO08oaT0wO2k8Yi5MO2krKylNLjNwKGJbaV0saCw2KGspe2cuVShkLj"
"NqP2tbZC4zal18fCIiOmtbMF0pfSk7SCBjPT09ZS5MLTF8fCFnLkw/ZzphKGcsYysxKX0oW2ZdLDA"
"pfTsxNS5aLjFwPTYoZixlKXtIIEouWChlWzBdKX07MTUuWi5XPTYoZixlKXtIIEouWChlKX07MTUu"
"Wi5YPTYoZil7SyBlPW4uWC4xcChKLDE0KSxhO0koZSl7SSgheCYmZS5MPjEmJnAoZSwiIik+LTEpe"
"2E9MTUoSi4xbSxuLlEuVyh0KEopLCJnIiwiIikpO24uUS5XKGYuMWEoZS5QKSxhLDYoKXtPKEsgYz"
"0xO2M8MTQuTC0yO2MrKylJKDE0W2NdPT09MWQpZVtjXT0xZH0pfUkoSi4xdyYmSi4xdy4xOSlPKEs"
"gYj0xO2I8ZS5MO2IrKylJKGE9Si4xdy4xOVtiLTFdKWVbYV09ZVtiXTshRCYmSi4xSiYmIWVbMF0u"
"TCYmSi4xMj5lLlAmJkouMTItLX1IIGV9O0koIUQpMTUuWi4xQT02KGYpeyhmPW4uWC5XKEosZikpJ"
"iZKLjFKJiYhZlswXS5MJiZKLjEyPmYuUCYmSi4xMi0tO0ghIWZ9OzFyLlouMUM9NihmKXtNLjFSKG"
"YpfHwoZj0xNShmKSk7SShmLjFKKXtLIGU9bi4xQy4xcChKLDE0KTtmLjEyPTA7SCBlfUggZi5YKEo"
"pfTsxci5aLlE9NihmLGUpe0sgYT1NLjFSKGYpLGIsYztJKGEmJjFqIGUuNTgoKT09PSIzZiImJmUu"
"MWkoIiR7Iik9PT0tMSYmeSlIIG4uUS4xcChKLDE0KTtJKGEpe0koZi4xdyliPWYuMXcuMTl9WSBmK"
"z0iIjtJKDFqIGU9PT0iNiIpYz1uLlEuVyhKLGYsNigpe0koYil7MTRbMF09MWYgMXIoMTRbMF0pO0"
"8oSyBkPTA7ZDxiLkw7ZCsrKUkoYltkXSkxNFswXVtiW2RdXT0xNFtkKzFdfUkoYSYmZi4xSilmLjE"
"yPTE0WzE0LkwtMl0rMTRbMF0uTDtIIGUuMXAoTiwxNCl9KTtZe2M9SisiIjtjPW4uUS5XKGMsZiw2"
"KCl7SyBkPTE0O0ggbi5RLlcoZSxDLDYoaCxnLGkpe0koZyk1YihnKXsyNCIkIjpIIiQiOzI0IiYiO"
"kggZFswXTsyNCJgIjpIIGRbZC5MLTFdLjFhKDAsZFtkLkwtMl0pOzI0IlwnIjpIIGRbZC5MLTFdLj"
"FhKGRbZC5MLTJdK2RbMF0uTCk7NWE6aT0iIjtnPStnO0koIWcpSCBoO08oO2c+ZC5MLTM7KXtpPTF"
"yLlouMWEuVyhnLC0xKStpO2c9MVEuM2koZy8xMCl9SChnP2RbZ118fCIiOiIkIikraX1Ze2c9K2k7"
"SShnPD1kLkwtMylIIGRbZ107Zz1iP3AoYixpKTotMTtIIGc+LTE/ZFtnKzFdOmh9fSl9KX1JKGEmJ"
"mYuMUopZi4xMj0wO0ggY307MXIuWi4xZT02KGYsZSl7SSghTS4xUihmKSlIIG4uMWUuMXAoSiwxNC"
"k7SyBhPUorIiIsYj1bXSxjPTAsZCxoO0koZT09PTFkfHwrZTwwKWU9NUQ7WXtlPTFRLjNpKCtlKTt"
"JKCFlKUhbXX1PKGY9TS4zYyhmKTtkPWYuWChhKTspe0koZi4xMj5jKXtiLlUoYS4xYShjLGQuUCkp"
"O2QuTD4xJiZkLlA8YS5MJiYzYi5aLlUuMXAoYixkLjFhKDEpKTtoPWRbMF0uTDtjPWYuMTI7SShiL"
"kw+PWUpMU59Zi4xMj09PWQuUCYmZi4xMisrfUkoYz09PWEuTCl7SSghbi4xQS5XKGYsIiIpfHxoKW"
"IuVSgiIil9WSBiLlUoYS4xYShjKSk7SCBiLkw+ZT9iLjFhKDAsZSk6Yn07TS4xaCgvXFwoXFw/I1t"
"eKV0qXFwpLyw2KGYpe0ggbi4xQS5XKEEsZi4yUy4xYShmLlArZlswXS5MKSk/IiI6Iig/OikifSk7"
"TS4xaCgvXFwoKD8hXFw/KS8sNigpe0ouMTkuVShOKTtIIigifSk7TS4xaCgvXFwoXFw/PChbJFxcd"
"10rKT4vLDYoZil7Si4xOS5VKGZbMV0pO0ouMk49UjtIIigifSk7TS4xaCgvXFxcXGs8KFtcXHckXS"
"spPi8sNihmKXtLIGU9cChKLjE5LGZbMV0pO0ggZT4tMT8iXFxcXCIrKGUrMSkrKDNSKGYuMlMuM2E"
"oZi5QK2ZbMF0uTCkpPyIiOiIoPzopIik6ZlswXX0pO00uMWgoL1xcW1xcXj9dLyw2KGYpe0ggZlsw"
"XT09PSJbXSI/IlxcXFxiXFxcXEIiOiJbXFxcXHNcXFxcU10ifSk7TS4xaCgvXlxcKFxcPyhbNUFdK"
"ylcXCkvLDYoZil7Si4zZChmWzFdKTtIIiJ9KTtNLjFoKC8oPzpcXHMrfCMuKikrLyw2KGYpe0ggbi"
"4xQS5XKEEsZi4yUy4xYShmLlArZlswXS5MKSk/IiI6Iig/OikifSxNLjFCLDYoKXtIIEouMksoIng"
"iKX0pO00uMWgoL1xcLi8sNigpe0giW1xcXFxzXFxcXFNdIn0sTS4xQiw2KCl7SCBKLjJLKCJzIil9"
"KX0pKCk7MWogMmUhPSIxZCImJigyZS5NPU0pO0sgMXY9NigpezYgcihhLGIpe2EuMWwuMWkoYikhP"
"S0xfHwoYS4xbCs9IiAiK2IpfTYgdChhKXtIIGEuMWkoIjNlIik9PTA/YToiM2UiK2F9NiBCKGEpe0"
"ggZS4xWS4yQVt0KGEpXX02IHAoYSxiLGMpe0koYT09TilIIE47SyBkPWMhPVI/YS4zRzpbYS4yR10"
"saD17IiMiOiIxYyIsIi4iOiIxbCJ9W2IuMW8oMCwxKV18fCIzaCIsZyxpO2c9aCE9IjNoIj9iLjFv"
"KDEpOmIuNXUoKTtJKChhW2hdfHwiIikuMWkoZykhPS0xKUggYTtPKGE9MDtkJiZhPGQuTCYmaT09T"
"jthKyspaT1wKGRbYV0sYixjKTtIIGl9NiBDKGEsYil7SyBjPXt9LGQ7TyhkIDJnIGEpY1tkXT1hW2"
"RdO08oZCAyZyBiKWNbZF09YltkXTtIIGN9NiB3KGEsYixjLGQpezYgaChnKXtnPWd8fDFQLjV5O0k"
"oIWcuMUYpe2cuMUY9Zy41MjtnLjNOPTYoKXtKLjV3PTExfX1jLlcoZHx8MVAsZyl9YS4zZz9hLjNn"
"KCI0VSIrYixoKTphLjR5KGIsaCwxMSl9NiBBKGEsYil7SyBjPWUuMVkuMmosZD1OO0koYz09Til7Y"
"z17fTtPKEsgaCAyZyBlLjFVKXtLIGc9ZS4xVVtoXTtkPWcuNHg7SShkIT1OKXtnLjFWPWguNHcoKT"
"tPKGc9MDtnPGQuTDtnKyspY1tkW2ddXT1ofX1lLjFZLjJqPWN9ZD1lLjFVW2NbYV1dO2Q9PU4mJmI"
"hPTExJiYxUC4xWChlLjEzLjF4LjFYKyhlLjEzLjF4LjNFK2EpKTtIIGR9NiB2KGEsYil7TyhLIGM9"
"YS4xZSgiXFxuIiksZD0wO2Q8Yy5MO2QrKyljW2RdPWIoY1tkXSxkKTtIIGMuMUsoIlxcbiIpfTYgd"
"ShhLGIpe0koYT09Tnx8YS5MPT0wfHxhPT0iXFxuIilIIGE7YT1hLlEoLzwvZywiJjF5OyIpO2E9YS"
"5RKC8gezIsfS9nLDYoYyl7TyhLIGQ9IiIsaD0wO2g8Yy5MLTE7aCsrKWQrPWUuMTMuMVc7SCBkKyI"
"gIn0pO0koYiE9TilhPXYoYSw2KGMpe0koYy5MPT0wKUgiIjtLIGQ9IiI7Yz1jLlEoL14oJjJzO3wg"
"KSsvLDYoaCl7ZD1oO0giIn0pO0koYy5MPT0wKUggZDtIIGQrXCc8MTcgMWc9IlwnK2IrXCciPlwnK"
"2MrIjwvMTc+In0pO0ggYX02IG4oYSxiKXthLjFlKCJcXG4iKTtPKEsgYz0iIixkPTA7ZDw1MDtkKy"
"spYys9IiAgICAgICAgICAgICAgICAgICAgIjtIIGE9dihhLDYoaCl7SShoLjFpKCJcXHQiKT09LTE"
"pSCBoO08oSyBnPTA7KGc9aC4xaSgiXFx0IikpIT0tMTspaD1oLjFvKDAsZykrYy4xbygwLGItZyVi"
"KStoLjFvKGcrMSxoLkwpO0ggaH0pfTYgeChhKXtIIGEuUSgvXlxccyt8XFxzKyQvZywiIil9NiBEK"
"GEsYil7SShhLlA8Yi5QKUgtMTtZIEkoYS5QPmIuUClIIDE7WSBJKGEuTDxiLkwpSC0xO1kgSShhLk"
"w+Yi5MKUggMTtIIDB9NiB5KGEsYil7NiBjKGspe0gga1swXX1PKEsgZD1OLGg9W10sZz1iLjJEP2I"
"uMkQ6YzsoZD1iLjFJLlgoYSkpIT1OOyl7SyBpPWcoZCxiKTtJKDFqIGk9PSIzZiIpaT1bMWYgZS4y"
"TChpLGQuUCxiLjIzKV07aD1oLjFPKGkpfUggaH02IEUoYSl7SyBiPS8oLiopKCgmMUc7fCYxeTspL"
"iopLztIIGEuUShlLjNBLjNNLDYoYyl7SyBkPSIiLGg9TjtJKGg9Yi5YKGMpKXtjPWhbMV07ZD1oWz"
"JdfUhcJzxhIDJoPSJcJytjK1wnIj5cJytjKyI8L2E+IitkfSl9NiB6KCl7TyhLIGE9MUUuMzYoIjF"
"rIiksYj1bXSxjPTA7YzxhLkw7YysrKWFbY10uM3M9PSIyMCImJmIuVShhW2NdKTtIIGJ9NiBmKGEp"
"e2E9YS4xRjtLIGI9cChhLCIuMjAiLFIpO2E9cChhLCIuM08iLFIpO0sgYz0xRS40aSgiM3QiKTtJK"
"CEoIWF8fCFifHxwKGEsIjN0IikpKXtCKGIuMWMpO3IoYiwiMW0iKTtPKEsgZD1hLjNHLGg9W10sZz"
"0wO2c8ZC5MO2crKyloLlUoZFtnXS40enx8ZFtnXS40QSk7aD1oLjFLKCJcXHIiKTtjLjM5KDFFLjR"
"EKGgpKTthLjM5KGMpO2MuMkMoKTtjLjRDKCk7dyhjLCI0dSIsNigpe2MuMkcuNEUoYyk7Yi4xbD1i"
"LjFsLlEoIjFtIiwiIil9KX19SSgxaiAzRiE9IjFkIiYmMWogTT09IjFkIilNPTNGKCJNIikuTTtLI"
"GU9ezJ2OnsiMWctMjciOiIiLCIyaS0xcyI6MSwiMnotMXMtMnQiOjExLDFNOk4sMXQ6TiwiNDItND"
"UiOlIsIjQzLTIyIjo0LDF1OlIsMTY6UiwiM1YtMTciOlIsMmw6MTEsIjQxLTQwIjpSLDJrOjExLCI"
"xei0xayI6MTF9LDEzOnsxVzoiJjJzOyIsMk06Uiw0NjoxMSw0NDoxMSwzNDoiNG4iLDF4OnsyMToi"
"NG8gMW0iLDJQOiI/IiwxWDoiMXZcXG5cXG4iLDNFOiI0clwndCA0dCAxRCBPOiAiLDRnOiI0bSA0Q"
"lwndCA1MSBPIDF6LTFrIDRGOiAiLDM3OlwnPCE0VCAxeiA0UyAiLS8vNFYvLzNIIDRXIDEuMCA0Wi"
"8vNFkiICIxWjovLzJ5LjNMLjNLLzRYLzNJLzNILzNJLTRQLjRKIj48MXogNEk9IjFaOi8vMnkuM0w"
"uM0svNEwvNUwiPjwzSj48NE4gMVotNE09IjVHLTVNIiA2Sz0iMk8vMXo7IDZKPTZJLTgiIC8+PDF0"
"PjZMIDF2PC8xdD48LzNKPjwzQiAxTD0iMjUtNk06NlEsNlAsNk8sNk4tNkY7NnktMmY6IzZ4OzJmO"
"iM2dzsyNS0yMjo2djsyTy0zRDozQzsiPjxUIDFMPSIyTy0zRDozQzszdy0zMjoxLjZ6OyI+PFQgMU"
"w9IjI1LTIyOjZBLTZFOyI+MXY8L1Q+PFQgMUw9IjI1LTIyOi42Qzszdy02Qjo2UjsiPjxUPjN2IDM"
"uMC43NiAoNzIgNzMgM3gpPC9UPjxUPjxhIDJoPSIxWjovLzN1LjJ3LzF2IiAxRj0iMzgiIDFMPSIy"
"ZjojM3kiPjFaOi8vM3UuMncvMXY8L2E+PC9UPjxUPjcwIDE3IDZVIDcxLjwvVD48VD42VCA2WC0ze"
"CA2WSA2RC48L1Q+PC9UPjxUPjZ0IDYxIDYwIEogMWssIDVaIDxhIDJoPSI2dTovLzJ5LjYyLjJ3Lz"
"YzLTY2LzY1PzY0PTVYLTVXJjVQPTVPIiAxTD0iMmY6IzN5Ij41UjwvYT4gNVYgPDJSLz41VSA1VCA"
"1UyE8L1Q+PC9UPjwvM0I+PC8xej5cJ319LDFZOnsyajpOLDJBOnt9fSwxVTp7fSwzQTp7Nm46L1xc"
"L1xcKltcXHNcXFNdKj9cXCpcXC8vMmMsNm06L1xcL1xcLy4qJC8yYyw2bDovIy4qJC8yYyw2azovI"
"ihbXlxcXFwiXFxuXXxcXFxcLikqIi9nLDZvOi9cJyhbXlxcXFxcJ1xcbl18XFxcXC4pKlwnL2csNn"
"A6MWYgTShcJyIoW15cXFxcXFxcXCJdfFxcXFxcXFxcLikqIlwnLCIzeiIpLDZzOjFmIE0oIlwnKFt"
"eXFxcXFxcXFxcJ118XFxcXFxcXFwuKSpcJyIsIjN6IiksNnE6LygmMXk7fDwpIS0tW1xcc1xcU10q"
"Py0tKCYxRzt8PikvMmMsM006L1xcdys6XFwvXFwvW1xcdy0uXFwvPyUmPTpAO10qL2csNmE6ezE4O"
"i8oJjF5O3w8KVxcPz0/L2csMWI6L1xcPygmMUc7fD4pL2d9LDY5OnsxODovKCYxeTt8PCklPT8vZy"
"wxYjovJSgmMUc7fD4pL2d9LDZkOnsxODovKCYxeTt8PClcXHMqMWsuKj8oJjFHO3w+KS8yVCwxYjo"
"vKCYxeTt8PClcXC9cXHMqMWtcXHMqKCYxRzt8PikvMlR9fSwxNjp7MUg6NihhKXs2IGIoaSxrKXtI"
"IGUuMTYuMm8oaSxrLGUuMTMuMXhba10pfU8oSyBjPVwnPFQgMWc9IjE2Ij5cJyxkPWUuMTYuMngsa"
"D1kLjJYLGc9MDtnPGguTDtnKyspYys9KGRbaFtnXV0uMUh8fGIpKGEsaFtnXSk7Yys9IjwvVD4iO0"
"ggY30sMm86NihhLGIsYyl7SFwnPDJXPjxhIDJoPSIjIiAxZz0iNmUgNmhcJytiKyIgIitiK1wnIj5"
"cJytjKyI8L2E+PC8yVz4ifSwyYjo2KGEpe0sgYj1hLjFGLGM9Yi4xbHx8IiI7Yj1CKHAoYiwiLjIw"
"IixSKS4xYyk7SyBkPTYoaCl7SChoPTE1KGgrIjZmKFxcXFx3KykiKS5YKGMpKT9oWzFdOk59KCI2Z"
"yIpO2ImJmQmJmUuMTYuMnhbZF0uMkIoYik7YS4zTigpfSwyeDp7Mlg6WyIyMSIsIjJQIl0sMjE6ez"
"FIOjYoYSl7SShhLlYoIjJsIikhPVIpSCIiO0sgYj1hLlYoIjF0Iik7SCBlLjE2LjJvKGEsIjIxIix"
"iP2I6ZS4xMy4xeC4yMSl9LDJCOjYoYSl7YT0xRS42aih0KGEuMWMpKTthLjFsPWEuMWwuUSgiNDci"
"LCIiKX19LDJQOnsyQjo2KCl7SyBhPSI2OD0wIjthKz0iLCAxOD0iKygzMS4zMC0zMykvMisiLCAzM"
"j0iKygzMS4yWi0yWSkvMisiLCAzMD0zMywgMlo9MlkiO2E9YS5RKC9eLC8sIiIpO2E9MVAuNlooIi"
"IsIjM4IixhKTthLjJDKCk7SyBiPWEuMUU7Yi42VyhlLjEzLjF4LjM3KTtiLjZWKCk7YS4yQygpfX1"
"9fSwzNTo2KGEsYil7SyBjO0koYiljPVtiXTtZe2M9MUUuMzYoZS4xMy4zNCk7TyhLIGQ9W10saD0w"
"O2g8Yy5MO2grKylkLlUoY1toXSk7Yz1kfWM9YztkPVtdO0koZS4xMy4yTSljPWMuMU8oeigpKTtJK"
"GMuTD09PTApSCBkO08oaD0wO2g8Yy5MO2grKyl7TyhLIGc9Y1toXSxpPWEsaz1jW2hdLjFsLGo9M1"
"cgMCxsPXt9LG09MWYgTSgiXlxcXFxbKD88MlY+KC4qPykpXFxcXF0kIikscz0xZiBNKCIoPzwyNz5"
"bXFxcXHctXSspXFxcXHMqOlxcXFxzKig/PDFUPltcXFxcdy0lI10rfFxcXFxbLio/XFxcXF18XFwi"
"Lio/XFwifFwnLio/XCcpXFxcXHMqOz8iLCJnIik7KGo9cy5YKGspKSE9Tjspe0sgbz1qLjFULlEoL"
"15bXCciXXxbXCciXSQvZywiIik7SShvIT1OJiZtLjFBKG8pKXtvPW0uWChvKTtvPW8uMlYuTD4wP2"
"8uMlYuMWUoL1xccyosXFxzKi8pOltdfWxbai4yN109b31nPXsxRjpnLDFuOkMoaSxsKX07Zy4xbi4"
"xRCE9TiYmZC5VKGcpfUggZH0sMU06NihhLGIpe0sgYz1KLjM1KGEsYiksZD1OLGg9ZS4xMztJKGMu"
"TCE9PTApTyhLIGc9MDtnPGMuTDtnKyspe2I9Y1tnXTtLIGk9Yi4xRixrPWIuMW4saj1rLjFELGw7S"
"ShqIT1OKXtJKGtbIjF6LTFrIl09PSJSInx8ZS4ydlsiMXotMWsiXT09Uil7ZD0xZiBlLjRsKGopO2"
"o9IjRPIn1ZIEkoZD1BKGopKWQ9MWYgZDtZIDZIO2w9aS4zWDtJKGguMk0pe2w9bDtLIG09eChsKSx"
"zPTExO0kobS4xaSgiPCFbNkdbIik9PTApe209bS40aCg5KTtzPVJ9SyBvPW0uTDtJKG0uMWkoIl1d"
"XFw+Iik9PW8tMyl7bT1tLjRoKDAsby0zKTtzPVJ9bD1zP206bH1JKChpLjF0fHwiIikhPSIiKWsuM"
"XQ9aS4xdDtrLjFEPWo7ZC4yUShrKTtiPWQuMkYobCk7SSgoaS4xY3x8IiIpIT0iIiliLjFjPWkuMW"
"M7aS4yRy43NChiLGkpfX19LDJFOjYoYSl7dygxUCwiNGsiLDYoKXtlLjFNKGEpfSl9fTtlLjJFPWU"
"uMkU7ZS4xTT1lLjFNO2UuMkw9NihhLGIsYyl7Si4xVD1hO0ouUD1iO0ouTD1hLkw7Si4yMz1jO0ou"
"MVY9Tn07ZS4yTC5aLjFxPTYoKXtIIEouMVR9O2UuNGw9NihhKXs2IGIoaixsKXtPKEsgbT0wO208a"
"i5MO20rKylqW21dLlArPWx9SyBjPUEoYSksZCxoPTFmIGUuMVUuNVksZz1KLGk9IjJGIDFIIDJRIi"
"4xZSgiICIpO0koYyE9Til7ZD0xZiBjO08oSyBrPTA7azxpLkw7aysrKSg2KCl7SyBqPWlba107Z1t"
"qXT02KCl7SCBoW2pdLjFwKGgsMTQpfX0pKCk7ZC4yOD09Tj8xUC4xWChlLjEzLjF4LjFYKyhlLjEz"
"LjF4LjRnK2EpKTpoLjJKLlUoezFJOmQuMjguMTcsMkQ6NihqKXtPKEsgbD1qLjE3LG09W10scz1kL"
"jJKLG89ai5QK2ouMTguTCxGPWQuMjgscSxHPTA7RzxzLkw7RysrKXtxPXkobCxzW0ddKTtiKHEsby"
"k7bT1tLjFPKHEpfUkoRi4xOCE9TiYmai4xOCE9Til7cT15KGouMTgsRi4xOCk7YihxLGouUCk7bT1"
"tLjFPKHEpfUkoRi4xYiE9TiYmai4xYiE9Til7cT15KGouMWIsRi4xYik7YihxLGouUCtqWzBdLjVR"
"KGouMWIpKTttPW0uMU8ocSl9TyhqPTA7ajxtLkw7aisrKW1bal0uMVY9Yy4xVjtIIG19fSl9fTtlL"
"jRqPTYoKXt9O2UuNGouWj17Vjo2KGEsYil7SyBjPUouMW5bYV07Yz1jPT1OP2I6YztLIGQ9eyJSIj"
"pSLCIxMSI6MTF9W2NdO0ggZD09Tj9jOmR9LDNZOjYoYSl7SCAxRS40aShhKX0sNGM6NihhLGIpe0s"
"gYz1bXTtJKGEhPU4pTyhLIGQ9MDtkPGEuTDtkKyspSSgxaiBhW2RdPT0iMm0iKWM9Yy4xTyh5KGIs"
"YVtkXSkpO0ggSi40ZShjLjZiKEQpKX0sNGU6NihhKXtPKEsgYj0wO2I8YS5MO2IrKylJKGFbYl0hP"
"T1OKU8oSyBjPWFbYl0sZD1jLlArYy5MLGg9YisxO2g8YS5MJiZhW2JdIT09TjtoKyspe0sgZz1hW2"
"hdO0koZyE9PU4pSShnLlA+ZCkxTjtZIEkoZy5QPT1jLlAmJmcuTD5jLkwpYVtiXT1OO1kgSShnLlA"
"+PWMuUCYmZy5QPGQpYVtoXT1OfUggYX0sNGQ6NihhKXtLIGI9W10sYz0ydShKLlYoIjJpLTFzIikp"
"O3YoYSw2KGQsaCl7Yi5VKGgrYyl9KTtIIGJ9LDNVOjYoYSl7SyBiPUouVigiMU0iLFtdKTtJKDFqI"
"GIhPSIybSImJmIuVT09TiliPVtiXTthOnthPWEuMXEoKTtLIGM9M1cgMDtPKGM9Yz0xUS42YyhjfH"
"wwLDApO2M8Yi5MO2MrKylJKGJbY109PWEpe2I9YzsxTiBhfWI9LTF9SCBiIT0tMX0sMnI6NihhLGI"
"sYyl7YT1bIjFzIiwiNmkiK2IsIlAiK2EsIjZyIisoYiUyPT0wPzE6MikuMXEoKV07Si4zVShiKSYm"
"YS5VKCI2NyIpO2I9PTAmJmEuVSgiMU4iKTtIXCc8VCAxZz0iXCcrYS4xSygiICIpK1wnIj5cJytjK"
"yI8L1Q+In0sM1E6NihhLGIpe0sgYz0iIixkPWEuMWUoIlxcbiIpLkwsaD0ydShKLlYoIjJpLTFzIi"
"kpLGc9Si5WKCIyei0xcy0ydCIpO0koZz09UilnPShoK2QtMSkuMXEoKS5MO1kgSSgzUihnKT09Uil"
"nPTA7TyhLIGk9MDtpPGQ7aSsrKXtLIGs9Yj9iW2ldOmgraSxqO0koaz09MClqPWUuMTMuMVc7WXtq"
"PWc7TyhLIGw9ay4xcSgpO2wuTDxqOylsPSIwIitsO2o9bH1hPWo7Yys9Si4ycihpLGssYSl9SCBjf"
"Sw0OTo2KGEsYil7YT14KGEpO0sgYz1hLjFlKCJcXG4iKTtKLlYoIjJ6LTFzLTJ0Iik7SyBkPTJ1KE"
"ouVigiMmktMXMiKSk7YT0iIjtPKEsgaD1KLlYoIjFEIiksZz0wO2c8Yy5MO2crKyl7SyBpPWNbZ10"
"saz0vXigmMnM7fFxccykrLy5YKGkpLGo9TixsPWI/YltnXTpkK2c7SShrIT1OKXtqPWtbMF0uMXEo"
"KTtpPWkuMW8oai5MKTtqPWouUSgiICIsZS4xMy4xVyl9aT14KGkpO0koaS5MPT0wKWk9ZS4xMy4xV"
"zthKz1KLjJyKGcsbCwoaiE9Tj9cJzwxNyAxZz0iXCcraCtcJyA1TiI+XCcraisiPC8xNz4iOiIiKS"
"tpKX1IIGF9LDRmOjYoYSl7SCBhPyI8NGE+IithKyI8LzRhPiI6IiJ9LDRiOjYoYSxiKXs2IGMobCl"
"7SChsPWw/bC4xVnx8ZzpnKT9sKyIgIjoiIn1PKEsgZD0wLGg9IiIsZz1KLlYoIjFEIiwiIiksaT0w"
"O2k8Yi5MO2krKyl7SyBrPWJbaV0sajtJKCEoaz09PU58fGsuTD09PTApKXtqPWMoayk7aCs9dShhL"
"jFvKGQsay5QLWQpLGorIjQ4IikrdShrLjFULGoray4yMyk7ZD1rLlAray5MKyhrLjc1fHwwKX19aC"
"s9dShhLjFvKGQpLGMoKSsiNDgiKTtIIGh9LDFIOjYoYSl7SyBiPSIiLGM9WyIyMCJdLGQ7SShKLlY"
"oIjJrIik9PVIpSi4xbi4xNj1KLjFuLjF1PTExOzFsPSIyMCI7Si5WKCIybCIpPT1SJiZjLlUoIjQ3"
"Iik7SSgoMXU9Si5WKCIxdSIpKT09MTEpYy5VKCI2UyIpO2MuVShKLlYoIjFnLTI3IikpO2MuVShKL"
"lYoIjFEIikpO2E9YS5RKC9eWyBdKltcXG5dK3xbXFxuXSpbIF0qJC9nLCIiKS5RKC9cXHIvZywiIC"
"IpO2I9Si5WKCI0My0yMiIpO0koSi5WKCI0Mi00NSIpPT1SKWE9bihhLGIpO1l7TyhLIGg9IiIsZz0"
"wO2c8YjtnKyspaCs9IiAiO2E9YS5RKC9cXHQvZyxoKX1hPWE7YTp7Yj1hPWE7aD0vPDJSXFxzKlxc"
"Lz8+fCYxeTsyUlxccypcXC8/JjFHOy8yVDtJKGUuMTMuNDY9PVIpYj1iLlEoaCwiXFxuIik7SShlL"
"jEzLjQ0PT1SKWI9Yi5RKGgsIiIpO2I9Yi4xZSgiXFxuIik7aD0vXlxccyovO2c9NFE7TyhLIGk9MD"
"tpPGIuTCYmZz4wO2krKyl7SyBrPWJbaV07SSh4KGspLkwhPTApe2s9aC5YKGspO0koaz09Til7YT1"
"hOzFOIGF9Zz0xUS40cShrWzBdLkwsZyl9fUkoZz4wKU8oaT0wO2k8Yi5MO2krKyliW2ldPWJbaV0u"
"MW8oZyk7YT1iLjFLKCJcXG4iKX1JKDF1KWQ9Si40ZChhKTtiPUouNGMoSi4ySixhKTtiPUouNGIoY"
"SxiKTtiPUouNDkoYixkKTtJKEouVigiNDEtNDAiKSliPUUoYik7MWogMkghPSIxZCImJjJILjNTJi"
"YySC4zUy4xQygvNXMvKSYmYy5VKCI1dCIpO0ggYj1cJzxUIDFjPSJcJyt0KEouMWMpK1wnIiAxZz0"
"iXCcrYy4xSygiICIpK1wnIj5cJysoSi5WKCIxNiIpP2UuMTYuMUgoSik6IiIpK1wnPDNaIDV6PSIw"
"IiA1SD0iMCIgNUo9IjAiPlwnK0ouNGYoSi5WKCIxdCIpKSsiPDNUPjwzUD4iKygxdT9cJzwyZCAxZ"
"z0iMXUiPlwnK0ouM1EoYSkrIjwvMmQ+IjoiIikrXCc8MmQgMWc9IjE3Ij48VCAxZz0iM08iPlwnK2"
"IrIjwvVD48LzJkPjwvM1A+PC8zVD48LzNaPjwvVD4ifSwyRjo2KGEpe0koYT09PU4pYT0iIjtKLjE"
"3PWE7SyBiPUouM1koIlQiKTtiLjNYPUouMUgoYSk7Si5WKCIxNiIpJiZ3KHAoYiwiLjE2IiksIjVj"
"IixlLjE2LjJiKTtKLlYoIjNWLTE3IikmJncocChiLCIuMTciKSwiNTYiLGYpO0ggYn0sMlE6NihhK"
"XtKLjFjPSIiKzFRLjVkKDFRLjVuKCkqNWspLjFxKCk7ZS4xWS4yQVt0KEouMWMpXT1KO0ouMW49Qy"
"hlLjJ2LGF8fHt9KTtJKEouVigiMmsiKT09UilKLjFuLjE2PUouMW4uMXU9MTF9LDVqOjYoYSl7YT1"
"hLlEoL15cXHMrfFxccyskL2csIiIpLlEoL1xccysvZywifCIpO0giXFxcXGIoPzoiK2ErIilcXFxc"
"YiJ9LDVmOjYoYSl7Si4yOD17MTg6ezFJOmEuMTgsMjM6IjFrIn0sMWI6ezFJOmEuMWIsMjM6IjFrI"
"n0sMTc6MWYgTSgiKD88MTg+IithLjE4LjFtKyIpKD88MTc+Lio/KSg/PDFiPiIrYS4xYi4xbSsiKS"
"IsIjVvIil9fX07SCBlfSgpOzFqIDJlIT0iMWQiJiYoMmUuMXY9MXYpOycsNjIsNDQxLCd8fHx8fHx"
"mdW5jdGlvbnx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHxyZXR1cm58aWZ8dGhp"
"c3x2YXJ8bGVuZ3RofFhSZWdFeHB8bnVsbHxmb3J8aW5kZXh8cmVwbGFjZXx0cnVlfHxkaXZ8cHVza"
"HxnZXRQYXJhbXxjYWxsfGV4ZWN8ZWxzZXxwcm90b3R5cGV8fGZhbHNlfGxhc3RJbmRleHxjb25maW"
"d8YXJndW1lbnRzfFJlZ0V4cHx0b29sYmFyfGNvZGV8bGVmdHxjYXB0dXJlTmFtZXN8c2xpY2V8cml"
"naHR8aWR8dW5kZWZpbmVkfHNwbGl0fG5ld3xjbGFzc3xhZGRUb2tlbnxpbmRleE9mfHR5cGVvZnxz"
"Y3JpcHR8Y2xhc3NOYW1lfHNvdXJjZXxwYXJhbXN8c3Vic3RyfGFwcGx5fHRvU3RyaW5nfFN0cmluZ"
"3xsaW5lfHRpdGxlfGd1dHRlcnxTeW50YXhIaWdobGlnaHRlcnxfeHJlZ2V4cHxzdHJpbmdzfGx0fG"
"h0bWx8dGVzdHxPVVRTSURFX0NMQVNTfG1hdGNofGJydXNofGRvY3VtZW50fHRhcmdldHxndHxnZXR"
"IdG1sfHJlZ2V4fGdsb2JhbHxqb2lufHN0eWxlfGhpZ2hsaWdodHxicmVha3xjb25jYXR8d2luZG93"
"fE1hdGh8aXNSZWdFeHB8dGhyb3d8dmFsdWV8YnJ1c2hlc3xicnVzaE5hbWV8c3BhY2V8YWxlcnR8d"
"mFyc3xodHRwfHN5bnRheGhpZ2hsaWdodGVyfGV4cGFuZFNvdXJjZXxzaXplfGNzc3xjYXNlfGZvbn"
"R8RmF8bmFtZXxodG1sU2NyaXB0fGRBfGNhbnxoYW5kbGVyfGdtfHRkfGV4cG9ydHN8Y29sb3J8aW5"
"8aHJlZnxmaXJzdHxkaXNjb3ZlcmVkQnJ1c2hlc3xsaWdodHxjb2xsYXBzZXxvYmplY3R8Y2FjaGV8"
"Z2V0QnV0dG9uSHRtbHx0cmlnZ2VyfHBhdHRlcm58Z2V0TGluZUh0bWx8bmJzcHxudW1iZXJzfHBhc"
"nNlSW50fGRlZmF1bHRzfGNvbXxpdGVtc3x3d3d8cGFkfGhpZ2hsaWdodGVyc3xleGVjdXRlfGZvY3"
"VzfGZ1bmN8YWxsfGdldERpdnxwYXJlbnROb2RlfG5hdmlnYXRvcnxJTlNJREVfQ0xBU1N8cmVnZXh"
"MaXN0fGhhc0ZsYWd8TWF0Y2h8dXNlU2NyaXB0VGFnc3xoYXNOYW1lZENhcHR1cmV8dGV4dHxoZWxw"
"fGluaXR8YnJ8aW5wdXR8Z2l8RXJyb3J8dmFsdWVzfHNwYW58bGlzdHwyNTB8aGVpZ2h0fHdpZHRof"
"HNjcmVlbnx0b3B8NTAwfHRhZ05hbWV8ZmluZEVsZW1lbnRzfGdldEVsZW1lbnRzQnlUYWdOYW1lfG"
"Fib3V0RGlhbG9nfF9ibGFua3xhcHBlbmRDaGlsZHxjaGFyQXR8QXJyYXl8Y29weUFzR2xvYmFsfHN"
"ldEZsYWd8aGlnaGxpZ2h0ZXJffHN0cmluZ3xhdHRhY2hFdmVudHxub2RlTmFtZXxmbG9vcnxiYWNr"
"cmVmfG91dHB1dHx0aGV8VHlwZUVycm9yfHN0aWNreXxaYXxpdGVyYXRlfGZyZWV6ZVRva2Vuc3xzY"
"29wZXx0eXBlfHRleHRhcmVhfGFsZXhnb3JiYXRjaGV2fHZlcnNpb258bWFyZ2lufDIwMTB8MDA1OD"
"k2fGdzfHJlZ2V4TGlifGJvZHl8Y2VudGVyfGFsaWdufG5vQnJ1c2h8cmVxdWlyZXxjaGlsZE5vZGV"
"zfERURHx4aHRtbDF8aGVhZHxvcmd8dzN8dXJsfHByZXZlbnREZWZhdWx0fGNvbnRhaW5lcnx0cnxn"
"ZXRMaW5lTnVtYmVyc0h0bWx8aXNOYU58dXNlckFnZW50fHRib2R5fGlzTGluZUhpZ2hsaWdodGVkf"
"HF1aWNrfHZvaWR8aW5uZXJIVE1MfGNyZWF0ZXx0YWJsZXxsaW5rc3xhdXRvfHNtYXJ0fHRhYnxzdH"
"JpcEJyc3x0YWJzfGJsb2dnZXJNb2RlfGNvbGxhcHNlZHxwbGFpbnxnZXRDb2RlTGluZXNIdG1sfGN"
"hcHRpb258Z2V0TWF0Y2hlc0h0bWx8ZmluZE1hdGNoZXN8ZmlndXJlT3V0TGluZU51bWJlcnN8cmVt"
"b3ZlTmVzdGVkTWF0Y2hlc3xnZXRUaXRsZUh0bWx8YnJ1c2hOb3RIdG1sU2NyaXB0fHN1YnN0cmluZ"
"3xjcmVhdGVFbGVtZW50fEhpZ2hsaWdodGVyfGxvYWR8SHRtbFNjcmlwdHxCcnVzaHxwcmV8ZXhwYW"
"5kfG11bHRpbGluZXxtaW58Q2FufGlnbm9yZUNhc2V8ZmluZHxibHVyfGV4dGVuZGVkfHRvTG93ZXJ"
"DYXNlfGFsaWFzZXN8YWRkRXZlbnRMaXN0ZW5lcnxpbm5lclRleHR8dGV4dENvbnRlbnR8d2Fzbnxz"
"ZWxlY3R8Y3JlYXRlVGV4dE5vZGV8cmVtb3ZlQ2hpbGR8b3B0aW9ufHNhbWV8ZnJhbWV8eG1sbnN8Z"
"HRkfHR3aWNlfDE5OTl8ZXF1aXZ8bWV0YXxodG1sc2NyaXB0fHRyYW5zaXRpb25hbHwxRTN8ZXhwZW"
"N0ZWR8UFVCTElDfERPQ1RZUEV8b258VzNDfFhIVE1MfFRSfEVOfFRyYW5zaXRpb25hbHx8Y29uZml"
"ndXJlZHxzcmNFbGVtZW50fE9iamVjdHxhZnRlcnxydW58ZGJsY2xpY2t8bWF0Y2hDaGFpbnx2YWx1"
"ZU9mfGNvbnN0cnVjdG9yfGRlZmF1bHR8c3dpdGNofGNsaWNrfHJvdW5kfGV4ZWNBdHxmb3JIdG1sU"
"2NyaXB0fHRva2VufGdpbXl8ZnVuY3Rpb25zfGdldEtleXdvcmRzfDFFNnxlc2NhcGV8d2l0aGlufH"
"JhbmRvbXxzZ2l8YW5vdGhlcnxmaW5hbGx5fHN1cHBseXxNU0lFfGllfHRvVXBwZXJDYXNlfGNhdGN"
"ofHJldHVyblZhbHVlfGRlZmluaXRpb258ZXZlbnR8Ym9yZGVyfGltc3h8Y29uc3RydWN0aW5nfG9u"
"ZXxJbmZpbml0eXxmcm9tfHdoZW58Q29udGVudHxjZWxscGFkZGluZ3xmbGFnc3xjZWxsc3BhY2luZ"
"3x0cnl8eGh0bWx8VHlwZXxzcGFjZXN8MjkzMDQwMnxob3N0ZWRfYnV0dG9uX2lkfGxhc3RJbmRleE"
"9mfGRvbmF0ZXxhY3RpdmV8ZGV2ZWxvcG1lbnR8a2VlcHx0b3x4Y2xpY2t8X3N8WG1sfHBsZWFzZXx"
"saWtlfHlvdXxwYXlwYWx8Y2dpfGNtZHx3ZWJzY3J8YmlufGhpZ2hsaWdodGVkfHNjcm9sbGJhcnN8"
"YXNwU2NyaXB0VGFnc3xwaHBTY3JpcHRUYWdzfHNvcnR8bWF4fHNjcmlwdFNjcmlwdFRhZ3N8dG9vb"
"GJhcl9pdGVtfF98Y29tbWFuZHxjb21tYW5kX3xudW1iZXJ8Z2V0RWxlbWVudEJ5SWR8ZG91YmxlUX"
"VvdGVkU3RyaW5nfHNpbmdsZUxpbmVQZXJsQ29tbWVudHN8c2luZ2xlTGluZUNDb21tZW50c3xtdWx"
"0aUxpbmVDQ29tbWVudHN8c2luZ2xlUXVvdGVkU3RyaW5nfG11bHRpTGluZURvdWJsZVF1b3RlZFN0"
"cmluZ3x4bWxDb21tZW50c3xhbHR8bXVsdGlMaW5lU2luZ2xlUXVvdGVkU3RyaW5nfElmfGh0dHBzf"
"DFlbXwwMDB8ZmZmfGJhY2tncm91bmR8NWVtfHh4fGJvdHRvbXw3NWVtfEdvcmJhdGNoZXZ8bGFyZ2"
"V8c2VyaWZ8Q0RBVEF8Y29udGludWV8dXRmfGNoYXJzZXR8Y29udGVudHxBYm91dHxmYW1pbHl8c2F"
"uc3xIZWx2ZXRpY2F8QXJpYWx8R2VuZXZhfDNlbXxub2d1dHRlcnxDb3B5cmlnaHR8c3ludGF4fGNs"
"b3NlfHdyaXRlfDIwMDR8QWxleHxvcGVufEphdmFTY3JpcHR8aGlnaGxpZ2h0ZXJ8SnVseXwwMnxyZ"
"XBsYWNlQ2hpbGR8b2Zmc2V0fDgzJy5zcGxpdCgnfCcpLDAse30pKQo%3D")

shbrushpython = ("data:application/x-javascript;base64,LyoqCiAqIFN5bnRheEhpZ2h"
"saWdodGVyCiAqIGh0dHA6Ly9hbGV4Z29yYmF0Y2hldi5jb20vU3ludGF4SGlnaGxpZ2h0ZXIKICoK"
"ICogU3ludGF4SGlnaGxpZ2h0ZXIgaXMgZG9uYXRpb253YXJlLiBJZiB5b3UgYXJlIHVzaW5nIGl0L"
"CBwbGVhc2UgZG9uYXRlLgogKiBodHRwOi8vYWxleGdvcmJhdGNoZXYuY29tL1N5bnRheEhpZ2hsaW"
"dodGVyL2RvbmF0ZS5odG1sCiAqCiAqIEB2ZXJzaW9uCiAqIDMuMC44MyAoSnVseSAwMiAyMDEwKQo"
"gKiAKICogQGNvcHlyaWdodAogKiBDb3B5cmlnaHQgKEMpIDIwMDQtMjAxMCBBbGV4IEdvcmJhdGNo"
"ZXYuCiAqCiAqIEBsaWNlbnNlCiAqIER1YWwgbGljZW5zZWQgdW5kZXIgdGhlIE1JVCBhbmQgR1BMI"
"GxpY2Vuc2VzLgogKi8KOyhmdW5jdGlvbigpCnsKCS8vIENvbW1vbkpTCgl0eXBlb2YocmVxdWlyZS"
"kgIT0gJ3VuZGVmaW5lZCcgPyBTeW50YXhIaWdobGlnaHRlciA9IHJlcXVpcmUoJ3NoQ29yZScpLlN"
"5bnRheEhpZ2hsaWdodGVyIDogbnVsbDsKCglmdW5jdGlvbiBCcnVzaCgpCgl7CgkJLy8gQ29udHJp"
"YnV0ZWQgYnkgR2hlb3JnaGUgTWlsYXMgYW5kIEFobWFkIFNoZXJpZgoJCgkJdmFyIGtleXdvcmRzI"
"D0gICdhbmQgYXNzZXJ0IGJyZWFrIGNsYXNzIGNvbnRpbnVlIGRlZiBkZWwgZWxpZiBlbHNlICcgKw"
"oJCQkJCQknZXhjZXB0IGV4ZWMgZmluYWxseSBmb3IgZnJvbSBnbG9iYWwgaWYgaW1wb3J0IGluIGl"
"zICcgKwoJCQkJCQknbGFtYmRhIG5vdCBvciBwYXNzIHByaW50IHJhaXNlIHJldHVybiB0cnkgeWll"
"bGQgd2hpbGUnOwoKCQl2YXIgZnVuY3MgPSAnX19pbXBvcnRfXyBhYnMgYWxsIGFueSBhcHBseSBiY"
"XNlc3RyaW5nIGJpbiBib29sIGJ1ZmZlciBjYWxsYWJsZSAnICsKCQkJCQknY2hyIGNsYXNzbWV0aG"
"9kIGNtcCBjb2VyY2UgY29tcGlsZSBjb21wbGV4IGRlbGF0dHIgZGljdCBkaXIgJyArCgkJCQkJJ2R"
"pdm1vZCBlbnVtZXJhdGUgZXZhbCBleGVjZmlsZSBmaWxlIGZpbHRlciBmbG9hdCBmb3JtYXQgZnJv"
"emVuc2V0ICcgKwoJCQkJCSdnZXRhdHRyIGdsb2JhbHMgaGFzYXR0ciBoYXNoIGhlbHAgaGV4IGlkI"
"GlucHV0IGludCBpbnRlcm4gJyArCgkJCQkJJ2lzaW5zdGFuY2UgaXNzdWJjbGFzcyBpdGVyIGxlbi"
"BsaXN0IGxvY2FscyBsb25nIG1hcCBtYXggbWluIG5leHQgJyArCgkJCQkJJ29iamVjdCBvY3Qgb3B"
"lbiBvcmQgcG93IHByaW50IHByb3BlcnR5IHJhbmdlIHJhd19pbnB1dCByZWR1Y2UgJyArCgkJCQkJ"
"J3JlbG9hZCByZXByIHJldmVyc2VkIHJvdW5kIHNldCBzZXRhdHRyIHNsaWNlIHNvcnRlZCBzdGF0a"
"WNtZXRob2QgJyArCgkJCQkJJ3N0ciBzdW0gc3VwZXIgdHVwbGUgdHlwZSB0eXBlIHVuaWNociB1bm"
"ljb2RlIHZhcnMgeHJhbmdlIHppcCc7CgoJCXZhciBzcGVjaWFsID0gICdOb25lIFRydWUgRmFsc2U"
"gc2VsZiBjbHMgY2xhc3NfJzsKCgkJdGhpcy5yZWdleExpc3QgPSBbCgkJCQl7IHJlZ2V4OiBTeW50"
"YXhIaWdobGlnaHRlci5yZWdleExpYi5zaW5nbGVMaW5lUGVybENvbW1lbnRzLCBjc3M6ICdjb21tZ"
"W50cycgfSwKCQkJCXsgcmVnZXg6IC9eXHMqQFx3Ky9nbSwgCQkJCQkJCQkJCWNzczogJ2RlY29yYX"
"RvcicgfSwKCQkJCXsgcmVnZXg6IC8oWydcIl17M30pKFteXDFdKSo/XDEvZ20sIAkJCQkJCWNzczo"
"gJ2NvbW1lbnRzJyB9LAoJCQkJeyByZWdleDogLyIoPyEiKSg/OlwufFxcXCJ8W15cIiJcbl0pKiIv"
"Z20sIAkJCQkJY3NzOiAnc3RyaW5nJyB9LAoJCQkJeyByZWdleDogLycoPyEnKSg/OlwufChcXFwnK"
"XxbXlwnJ1xuXSkqJy9nbSwgCQkJCWNzczogJ3N0cmluZycgfSwKCQkJCXsgcmVnZXg6IC9cK3xcLX"
"xcKnxcL3xcJXw9fD09L2dtLCAJCQkJCQkJY3NzOiAna2V5d29yZCcgfSwKCQkJCXsgcmVnZXg6IC9"
"cYlxkK1wuP1x3Ki9nLCAJCQkJCQkJCQljc3M6ICd2YWx1ZScgfSwKCQkJCXsgcmVnZXg6IG5ldyBS"
"ZWdFeHAodGhpcy5nZXRLZXl3b3JkcyhmdW5jcyksICdnbWknKSwJCWNzczogJ2Z1bmN0aW9ucycgf"
"SwKCQkJCXsgcmVnZXg6IG5ldyBSZWdFeHAodGhpcy5nZXRLZXl3b3JkcyhrZXl3b3JkcyksICdnbS"
"cpLCAJCWNzczogJ2tleXdvcmQnIH0sCgkJCQl7IHJlZ2V4OiBuZXcgUmVnRXhwKHRoaXMuZ2V0S2V"
"5d29yZHMoc3BlY2lhbCksICdnbScpLCAJCWNzczogJ2NvbG9yMScgfQoJCQkJXTsKCQkJCgkJdGhp"
"cy5mb3JIdG1sU2NyaXB0KFN5bnRheEhpZ2hsaWdodGVyLnJlZ2V4TGliLmFzcFNjcmlwdFRhZ3MpO"
"woJfTsKCglCcnVzaC5wcm90b3R5cGUJPSBuZXcgU3ludGF4SGlnaGxpZ2h0ZXIuSGlnaGxpZ2h0ZX"
"IoKTsKCUJydXNoLmFsaWFzZXMJPSBbJ3B5JywgJ3B5dGhvbiddOwoKCVN5bnRheEhpZ2hsaWdodGV"
"yLmJydXNoZXMuUHl0aG9uID0gQnJ1c2g7CgoJLy8gQ29tbW9uSlMKCXR5cGVvZihleHBvcnRzKSAh"
"PSAndW5kZWZpbmVkJyA/IGV4cG9ydHMuQnJ1c2ggPSBCcnVzaCA6IG51bGw7Cn0pKCk7Cg%3D%3D")

shcorecss = ("data:text/css;base64,LyoqCiAqIFN5bnRheEhpZ2hsaWdodGVyCiAqIGh0dHA"
"6Ly9hbGV4Z29yYmF0Y2hldi5jb20vU3ludGF4SGlnaGxpZ2h0ZXIKICoKICogU3ludGF4SGlnaGxp"
"Z2h0ZXIgaXMgZG9uYXRpb253YXJlLiBJZiB5b3UgYXJlIHVzaW5nIGl0LCBwbGVhc2UgZG9uYXRlL"
"gogKiBodHRwOi8vYWxleGdvcmJhdGNoZXYuY29tL1N5bnRheEhpZ2hsaWdodGVyL2RvbmF0ZS5odG"
"1sCiAqCiAqIEB2ZXJzaW9uCiAqIDMuMC44MyAoSnVseSAwMiAyMDEwKQogKiAKICogQGNvcHlyaWd"
"odAogKiBDb3B5cmlnaHQgKEMpIDIwMDQtMjAxMCBBbGV4IEdvcmJhdGNoZXYuCiAqCiAqIEBsaWNl"
"bnNlCiAqIER1YWwgbGljZW5zZWQgdW5kZXIgdGhlIE1JVCBhbmQgR1BMIGxpY2Vuc2VzLgogKi8KL"
"nN5bnRheGhpZ2hsaWdodGVyIGEsCi5zeW50YXhoaWdobGlnaHRlciBkaXYsCi5zeW50YXhoaWdobG"
"lnaHRlciBjb2RlLAouc3ludGF4aGlnaGxpZ2h0ZXIgdGFibGUsCi5zeW50YXhoaWdobGlnaHRlciB"
"0YWJsZSB0ZCwKLnN5bnRheGhpZ2hsaWdodGVyIHRhYmxlIHRyLAouc3ludGF4aGlnaGxpZ2h0ZXIg"
"dGFibGUgdGJvZHksCi5zeW50YXhoaWdobGlnaHRlciB0YWJsZSB0aGVhZCwKLnN5bnRheGhpZ2hsa"
"WdodGVyIHRhYmxlIGNhcHRpb24sCi5zeW50YXhoaWdobGlnaHRlciB0ZXh0YXJlYSB7CiAgLW1vei"
"1ib3JkZXItcmFkaXVzOiAwIDAgMCAwICFpbXBvcnRhbnQ7CiAgLXdlYmtpdC1ib3JkZXItcmFkaXV"
"zOiAwIDAgMCAwICFpbXBvcnRhbnQ7CiAgYmFja2dyb3VuZDogbm9uZSAhaW1wb3J0YW50OwogIGJv"
"cmRlcjogMCAhaW1wb3J0YW50OwogIGJvdHRvbTogYXV0byAhaW1wb3J0YW50OwogIGZsb2F0OiBub"
"25lICFpbXBvcnRhbnQ7CiAgaGVpZ2h0OiBhdXRvICFpbXBvcnRhbnQ7CiAgbGVmdDogYXV0byAhaW"
"1wb3J0YW50OwogIGxpbmUtaGVpZ2h0OiAxLjFlbSAhaW1wb3J0YW50OwogIG1hcmdpbjogMCAhaW1"
"wb3J0YW50OwogIG91dGxpbmU6IDAgIWltcG9ydGFudDsKICBvdmVyZmxvdzogdmlzaWJsZSAhaW1w"
"b3J0YW50OwogIHBhZGRpbmc6IDAgIWltcG9ydGFudDsKICBwb3NpdGlvbjogc3RhdGljICFpbXBvc"
"nRhbnQ7CiAgcmlnaHQ6IGF1dG8gIWltcG9ydGFudDsKICB0ZXh0LWFsaWduOiBsZWZ0ICFpbXBvcn"
"RhbnQ7CiAgdG9wOiBhdXRvICFpbXBvcnRhbnQ7CiAgdmVydGljYWwtYWxpZ246IGJhc2VsaW5lICF"
"pbXBvcnRhbnQ7CiAgd2lkdGg6IGF1dG8gIWltcG9ydGFudDsKICBib3gtc2l6aW5nOiBjb250ZW50"
"LWJveCAhaW1wb3J0YW50OwogIGZvbnQtZmFtaWx5OiAiQ29uc29sYXMiLCAiQml0c3RyZWFtIFZlc"
"mEgU2FucyBNb25vIiwgIkNvdXJpZXIgTmV3IiwgQ291cmllciwgbW9ub3NwYWNlICFpbXBvcnRhbn"
"Q7CiAgZm9udC13ZWlnaHQ6IG5vcm1hbCAhaW1wb3J0YW50OwogIGZvbnQtc3R5bGU6IG5vcm1hbCA"
"haW1wb3J0YW50OwogIGZvbnQtc2l6ZTogMWVtICFpbXBvcnRhbnQ7CiAgbWluLWhlaWdodDogaW5o"
"ZXJpdCAhaW1wb3J0YW50OwogIG1pbi1oZWlnaHQ6IGF1dG8gIWltcG9ydGFudDsKfQoKLnN5bnRhe"
"GhpZ2hsaWdodGVyIHsKICB3aWR0aDogMTAwJSAhaW1wb3J0YW50OwogIG1hcmdpbjogMWVtIDAgMW"
"VtIDAgIWltcG9ydGFudDsKICBwb3NpdGlvbjogcmVsYXRpdmUgIWltcG9ydGFudDsKICBvdmVyZmx"
"vdzogYXV0byAhaW1wb3J0YW50OwogIGZvbnQtc2l6ZTogMWVtICFpbXBvcnRhbnQ7Cn0KLnN5bnRh"
"eGhpZ2hsaWdodGVyLnNvdXJjZSB7CiAgb3ZlcmZsb3c6IGhpZGRlbiAhaW1wb3J0YW50Owp9Ci5ze"
"W50YXhoaWdobGlnaHRlciAuYm9sZCB7CiAgZm9udC13ZWlnaHQ6IGJvbGQgIWltcG9ydGFudDsKfQ"
"ouc3ludGF4aGlnaGxpZ2h0ZXIgLml0YWxpYyB7CiAgZm9udC1zdHlsZTogaXRhbGljICFpbXBvcnR"
"hbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyIC5saW5lIHsKICB3aGl0ZS1zcGFjZTogcHJlICFpbXBv"
"cnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyIHRhYmxlIHsKICB3aWR0aDogMTAwJSAhaW1wb3J0Y"
"W50Owp9Ci5zeW50YXhoaWdobGlnaHRlciB0YWJsZSBjYXB0aW9uIHsKICB0ZXh0LWFsaWduOiBsZW"
"Z0ICFpbXBvcnRhbnQ7CiAgcGFkZGluZzogLjVlbSAwIDAuNWVtIDFlbSAhaW1wb3J0YW50Owp9Ci5"
"zeW50YXhoaWdobGlnaHRlciB0YWJsZSB0ZC5jb2RlIHsKICB3aWR0aDogMTAwJSAhaW1wb3J0YW50"
"Owp9Ci5zeW50YXhoaWdobGlnaHRlciB0YWJsZSB0ZC5jb2RlIC5jb250YWluZXIgewogIHBvc2l0a"
"W9uOiByZWxhdGl2ZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciB0YWJsZSB0ZC5jb2"
"RlIC5jb250YWluZXIgdGV4dGFyZWEgewogIGJveC1zaXppbmc6IGJvcmRlci1ib3ggIWltcG9ydGF"
"udDsKICBwb3NpdGlvbjogYWJzb2x1dGUgIWltcG9ydGFudDsKICBsZWZ0OiAwICFpbXBvcnRhbnQ7"
"CiAgdG9wOiAwICFpbXBvcnRhbnQ7CiAgd2lkdGg6IDEwMCUgIWltcG9ydGFudDsKICBoZWlnaHQ6I"
"DEwMCUgIWltcG9ydGFudDsKICBib3JkZXI6IG5vbmUgIWltcG9ydGFudDsKICBiYWNrZ3JvdW5kOi"
"B3aGl0ZSAhaW1wb3J0YW50OwogIHBhZGRpbmctbGVmdDogMWVtICFpbXBvcnRhbnQ7CiAgb3ZlcmZ"
"sb3c6IGhpZGRlbiAhaW1wb3J0YW50OwogIHdoaXRlLXNwYWNlOiBwcmUgIWltcG9ydGFudDsKfQou"
"c3ludGF4aGlnaGxpZ2h0ZXIgdGFibGUgdGQuZ3V0dGVyIC5saW5lIHsKICB0ZXh0LWFsaWduOiBya"
"WdodCAhaW1wb3J0YW50OwogIHBhZGRpbmc6IDAgMC41ZW0gMCAxZW0gIWltcG9ydGFudDsKfQouc3"
"ludGF4aGlnaGxpZ2h0ZXIgdGFibGUgdGQuY29kZSAubGluZSB7CiAgcGFkZGluZzogMCAxZW0gIWl"
"tcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIubm9ndXR0ZXIgdGQuY29kZSAuY29udGFpbmVy"
"IHRleHRhcmVhLCAuc3ludGF4aGlnaGxpZ2h0ZXIubm9ndXR0ZXIgdGQuY29kZSAubGluZSB7CiAgc"
"GFkZGluZy1sZWZ0OiAwZW0gIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIuc2hvdyB7Ci"
"AgZGlzcGxheTogYmxvY2sgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIuY29sbGFwc2V"
"kIHRhYmxlIHsKICBkaXNwbGF5OiBub25lICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVy"
"LmNvbGxhcHNlZCAudG9vbGJhciB7CiAgcGFkZGluZzogMC4xZW0gMC44ZW0gMGVtIDAuOGVtICFpb"
"XBvcnRhbnQ7CiAgZm9udC1zaXplOiAxZW0gIWltcG9ydGFudDsKICBwb3NpdGlvbjogc3RhdGljIC"
"FpbXBvcnRhbnQ7CiAgd2lkdGg6IGF1dG8gIWltcG9ydGFudDsKICBoZWlnaHQ6IGF1dG8gIWltcG9"
"ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIuY29sbGFwc2VkIC50b29sYmFyIHNwYW4gewogIGRp"
"c3BsYXk6IGlubGluZSAhaW1wb3J0YW50OwogIG1hcmdpbi1yaWdodDogMWVtICFpbXBvcnRhbnQ7C"
"n0KLnN5bnRheGhpZ2hsaWdodGVyLmNvbGxhcHNlZCAudG9vbGJhciBzcGFuIGEgewogIHBhZGRpbm"
"c6IDAgIWltcG9ydGFudDsKICBkaXNwbGF5OiBub25lICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2h"
"saWdodGVyLmNvbGxhcHNlZCAudG9vbGJhciBzcGFuIGEuZXhwYW5kU291cmNlIHsKICBkaXNwbGF5"
"OiBpbmxpbmUgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLnRvb2xiYXIgewogIHBvc"
"2l0aW9uOiBhYnNvbHV0ZSAhaW1wb3J0YW50OwogIHJpZ2h0OiAxcHggIWltcG9ydGFudDsKICB0b3"
"A6IDFweCAhaW1wb3J0YW50OwogIHdpZHRoOiAxMXB4ICFpbXBvcnRhbnQ7CiAgaGVpZ2h0OiAxMXB"
"4ICFpbXBvcnRhbnQ7CiAgZm9udC1zaXplOiAxMHB4ICFpbXBvcnRhbnQ7CiAgei1pbmRleDogMTAg"
"IWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLnRvb2xiYXIgc3Bhbi50aXRsZSB7CiAgZ"
"GlzcGxheTogaW5saW5lICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyIC50b29sYmFyIG"
"EgewogIGRpc3BsYXk6IGJsb2NrICFpbXBvcnRhbnQ7CiAgdGV4dC1hbGlnbjogY2VudGVyICFpbXB"
"vcnRhbnQ7CiAgdGV4dC1kZWNvcmF0aW9uOiBub25lICFpbXBvcnRhbnQ7CiAgcGFkZGluZy10b3A6"
"IDFweCAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAudG9vbGJhciBhLmV4cGFuZFNvd"
"XJjZSB7CiAgZGlzcGxheTogbm9uZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5pZS"
"B7CiAgZm9udC1zaXplOiAuOWVtICFpbXBvcnRhbnQ7CiAgcGFkZGluZzogMXB4IDAgMXB4IDAgIWl"
"tcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIuaWUgLnRvb2xiYXIgewogIGxpbmUtaGVpZ2h0"
"OiA4cHggIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIuaWUgLnRvb2xiYXIgYSB7CiAgc"
"GFkZGluZy10b3A6IDBweCAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZy"
"AubGluZS5hbHQxIC5jb250ZW50LAouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLmxpbmUuYWx"
"0MiAuY29udGVudCwKLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIC5saW5lLmhpZ2hsaWdodGVk"
"IC5udW1iZXIsCi5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAubGluZS5oaWdobGlnaHRlZC5hb"
"HQxIC5jb250ZW50LAouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLmxpbmUuaGlnaGxpZ2h0ZW"
"QuYWx0MiAuY29udGVudCB7CiAgYmFja2dyb3VuZDogbm9uZSAhaW1wb3J0YW50Owp9Ci5zeW50YXh"
"oaWdobGlnaHRlci5wcmludGluZyAubGluZSAubnVtYmVyIHsKICBjb2xvcjogI2JiYmJiYiAhaW1w"
"b3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAubGluZSAuY29udGVudCB7CiAgY"
"29sb3I6IGJsYWNrICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIC50b2"
"9sYmFyIHsKICBkaXNwbGF5OiBub25lICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLnB"
"yaW50aW5nIGEgewogIHRleHQtZGVjb3JhdGlvbjogbm9uZSAhaW1wb3J0YW50Owp9Ci5zeW50YXho"
"aWdobGlnaHRlci5wcmludGluZyAucGxhaW4sIC5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAuc"
"GxhaW4gYSB7CiAgY29sb3I6IGJsYWNrICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLn"
"ByaW50aW5nIC5jb21tZW50cywgLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIC5jb21tZW50cyB"
"hIHsKICBjb2xvcjogIzAwODIwMCAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmlu"
"dGluZyAuc3RyaW5nLCAuc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLnN0cmluZyBhIHsKICBjb"
"2xvcjogYmx1ZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAua2V5d2"
"9yZCB7CiAgY29sb3I6ICMwMDY2OTkgIWltcG9ydGFudDsKICBmb250LXdlaWdodDogYm9sZCAhaW1"
"wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAucHJlcHJvY2Vzc29yIHsKICBj"
"b2xvcjogZ3JheSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAudmFya"
"WFibGUgewogIGNvbG9yOiAjYWE3NzAwICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLn"
"ByaW50aW5nIC52YWx1ZSB7CiAgY29sb3I6ICMwMDk5MDAgIWltcG9ydGFudDsKfQouc3ludGF4aGl"
"naGxpZ2h0ZXIucHJpbnRpbmcgLmZ1bmN0aW9ucyB7CiAgY29sb3I6ICNmZjE0OTMgIWltcG9ydGFu"
"dDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLmNvbnN0YW50cyB7CiAgY29sb3I6ICMwM"
"DY2Y2MgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLnNjcmlwdCB7Ci"
"AgZm9udC13ZWlnaHQ6IGJvbGQgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnR"
"pbmcgLmNvbG9yMSwgLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIC5jb2xvcjEgYSB7CiAgY29s"
"b3I6IGdyYXkgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLmNvbG9yM"
"iwgLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIC5jb2xvcjIgYSB7CiAgY29sb3I6ICNmZjE0OT"
"MgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLmNvbG9yMywgLnN5bnR"
"heGhpZ2hsaWdodGVyLnByaW50aW5nIC5jb2xvcjMgYSB7CiAgY29sb3I6IHJlZCAhaW1wb3J0YW50"
"Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAuYnJlYWssIC5zeW50YXhoaWdobGlnaHRlc"
"i5wcmludGluZyAuYnJlYWsgYSB7CiAgY29sb3I6IGJsYWNrICFpbXBvcnRhbnQ7Cn0K")

shthemedefault = ("data:text/css;base64,LyoqCiAqIFN5bnRheEhpZ2hsaWdodGVyCiAqIG"
"h0dHA6Ly9hbGV4Z29yYmF0Y2hldi5jb20vU3ludGF4SGlnaGxpZ2h0ZXIKICoKICogU3ludGF4SGl"
"naGxpZ2h0ZXIgaXMgZG9uYXRpb253YXJlLiBJZiB5b3UgYXJlIHVzaW5nIGl0LCBwbGVhc2UgZG9u"
"YXRlLgogKiBodHRwOi8vYWxleGdvcmJhdGNoZXYuY29tL1N5bnRheEhpZ2hsaWdodGVyL2RvbmF0Z"
"S5odG1sCiAqCiAqIEB2ZXJzaW9uCiAqIDMuMC44MyAoSnVseSAwMiAyMDEwKQogKiAKICogQGNvcH"
"lyaWdodAogKiBDb3B5cmlnaHQgKEMpIDIwMDQtMjAxMCBBbGV4IEdvcmJhdGNoZXYuCiAqCiAqIEB"
"saWNlbnNlCiAqIER1YWwgbGljZW5zZWQgdW5kZXIgdGhlIE1JVCBhbmQgR1BMIGxpY2Vuc2VzLgog"
"Ki8KLnN5bnRheGhpZ2hsaWdodGVyIHsKICBiYWNrZ3JvdW5kLWNvbG9yOiB3aGl0ZSAhaW1wb3J0Y"
"W50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAubGluZS5hbHQxIHsKICBiYWNrZ3JvdW5kLWNvbG9yOi"
"B3aGl0ZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAubGluZS5hbHQyIHsKICBiYWN"
"rZ3JvdW5kLWNvbG9yOiB3aGl0ZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAubGlu"
"ZS5oaWdobGlnaHRlZC5hbHQxLCAuc3ludGF4aGlnaGxpZ2h0ZXIgLmxpbmUuaGlnaGxpZ2h0ZWQuY"
"Wx0MiB7CiAgYmFja2dyb3VuZC1jb2xvcjogI2UwZTBlMCAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaW"
"dobGlnaHRlciAubGluZS5oaWdobGlnaHRlZC5udW1iZXIgewogIGNvbG9yOiBibGFjayAhaW1wb3J"
"0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciB0YWJsZSBjYXB0aW9uIHsKICBjb2xvcjogYmxhY2sg"
"IWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLmd1dHRlciB7CiAgY29sb3I6ICNhZmFmY"
"WYgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLmd1dHRlciAubGluZSB7CiAgYm9yZG"
"VyLXJpZ2h0OiAzcHggc29saWQgIzZjZTI2YyAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHR"
"lciAuZ3V0dGVyIC5saW5lLmhpZ2hsaWdodGVkIHsKICBiYWNrZ3JvdW5kLWNvbG9yOiAjNmNlMjZj"
"ICFpbXBvcnRhbnQ7CiAgY29sb3I6IHdoaXRlICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdod"
"GVyLnByaW50aW5nIC5saW5lIC5jb250ZW50IHsKICBib3JkZXI6IG5vbmUgIWltcG9ydGFudDsKfQ"
"ouc3ludGF4aGlnaGxpZ2h0ZXIuY29sbGFwc2VkIHsKICBvdmVyZmxvdzogdmlzaWJsZSAhaW1wb3J"
"0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5jb2xsYXBzZWQgLnRvb2xiYXIgewogIGNvbG9yOiBi"
"bHVlICFpbXBvcnRhbnQ7CiAgYmFja2dyb3VuZDogd2hpdGUgIWltcG9ydGFudDsKICBib3JkZXI6I"
"DFweCBzb2xpZCAjNmNlMjZjICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLmNvbGxhcH"
"NlZCAudG9vbGJhciBhIHsKICBjb2xvcjogYmx1ZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGl"
"naHRlci5jb2xsYXBzZWQgLnRvb2xiYXIgYTpob3ZlciB7CiAgY29sb3I6IHJlZCAhaW1wb3J0YW50"
"Owp9Ci5zeW50YXhoaWdobGlnaHRlciAudG9vbGJhciB7CiAgY29sb3I6IHdoaXRlICFpbXBvcnRhb"
"nQ7CiAgYmFja2dyb3VuZDogIzZjZTI2YyAhaW1wb3J0YW50OwogIGJvcmRlcjogbm9uZSAhaW1wb3"
"J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAudG9vbGJhciBhIHsKICBjb2xvcjogd2hpdGUgIWl"
"tcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLnRvb2xiYXIgYTpob3ZlciB7CiAgY29sb3I6"
"IGJsYWNrICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyIC5wbGFpbiwgLnN5bnRheGhpZ"
"2hsaWdodGVyIC5wbGFpbiBhIHsKICBjb2xvcjogYmxhY2sgIWltcG9ydGFudDsKfQouc3ludGF4aG"
"lnaGxpZ2h0ZXIgLmNvbW1lbnRzLCAuc3ludGF4aGlnaGxpZ2h0ZXIgLmNvbW1lbnRzIGEgewogIGN"
"vbG9yOiAjMDA4MjAwICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyIC5zdHJpbmcsIC5z"
"eW50YXhoaWdobGlnaHRlciAuc3RyaW5nIGEgewogIGNvbG9yOiBibHVlICFpbXBvcnRhbnQ7Cn0KL"
"nN5bnRheGhpZ2hsaWdodGVyIC5rZXl3b3JkIHsKICBjb2xvcjogIzAwNjY5OSAhaW1wb3J0YW50Ow"
"p9Ci5zeW50YXhoaWdobGlnaHRlciAucHJlcHJvY2Vzc29yIHsKICBjb2xvcjogZ3JheSAhaW1wb3J"
"0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAudmFyaWFibGUgewogIGNvbG9yOiAjYWE3NzAwICFp"
"bXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyIC52YWx1ZSB7CiAgY29sb3I6ICMwMDk5MDAgI"
"WltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLmZ1bmN0aW9ucyB7CiAgY29sb3I6ICNmZj"
"E0OTMgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLmNvbnN0YW50cyB7CiAgY29sb3I"
"6ICMwMDY2Y2MgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLnNjcmlwdCB7CiAgZm9u"
"dC13ZWlnaHQ6IGJvbGQgIWltcG9ydGFudDsKICBjb2xvcjogIzAwNjY5OSAhaW1wb3J0YW50OwogI"
"GJhY2tncm91bmQtY29sb3I6IG5vbmUgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLm"
"NvbG9yMSwgLnN5bnRheGhpZ2hsaWdodGVyIC5jb2xvcjEgYSB7CiAgY29sb3I6IGdyYXkgIWltcG9"
"ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLmNvbG9yMiwgLnN5bnRheGhpZ2hsaWdodGVyIC5j"
"b2xvcjIgYSB7CiAgY29sb3I6ICNmZjE0OTMgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0Z"
"XIgLmNvbG9yMywgLnN5bnRheGhpZ2hsaWdodGVyIC5jb2xvcjMgYSB7CiAgY29sb3I6IHJlZCAhaW"
"1wb3J0YW50Owp9Cgouc3ludGF4aGlnaGxpZ2h0ZXIgLmtleXdvcmQgewogIGZvbnQtd2VpZ2h0OiB"
"ib2xkICFpbXBvcnRhbnQ7Cn0K")
