from cStringIO import StringIO
from traceback import print_exc
from pprint import pformat

from mako.template import Template

from webob import Response

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

pre code {
  display: block; padding: 0.5em;
  background: #F0F0F0;
}

pre code,
pre .ruby .subst,
pre .tag .title,
pre .lisp .title {
  color: black;
}

pre .string,
pre .title,
pre .constant,
pre .parent,
pre .tag .value,
pre .rules .value,
pre .rules .value .number,
pre .preprocessor,
pre .ruby .symbol,
pre .ruby .symbol .string,
pre .ruby .symbol .keyword,
pre .ruby .symbol .keymethods,
pre .instancevar,
pre .aggregate,
pre .template_tag,
pre .django .variable,
pre .smalltalk .class,
pre .addition,
pre .flow,
pre .stream,
pre .bash .variable,
pre .apache .tag,
pre .apache .cbracket,
pre .tex .command,
pre .tex .special,
pre .erlang_repl .function_or_atom {
  color: #800;
}

pre .comment,
pre .annotation,
pre .template_comment,
pre .diff .header,
pre .chunk {
  color: #888;
}

pre .number,
pre .date,
pre .regexp,
pre .literal,
pre .smalltalk .symbol,
pre .smalltalk .char,
pre .go .constant,
pre .change {
  color: #080;
}

pre .label,
pre .javadoc,
pre .ruby .string,
pre .decorator,
pre .filter .argument,
pre .localvars,
pre .array,
pre .attr_selector,
pre .important,
pre .pseudo,
pre .pi,
pre .doctype,
pre .deletion,
pre .envvar,
pre .shebang,
pre .apache .sqbracket,
pre .nginx .built_in,
pre .tex .formula,
pre .erlang_repl .reserved,
pre .input_number {
  color: #88F
}

pre .css .tag,
pre .javadoctag,
pre .phpdoc,
pre .yardoctag {
  font-weight: bold;
}

pre .keyword,
pre .id,
pre .phpdoc,
pre .title,
pre .built_in,
pre .aggregate,
pre .smalltalk .class,
pre .winutils,
pre .bash .variable,
pre .apache .tag,
pre .go .typename,
pre .tex .command {
  font-weight: bold;
}

pre .nginx .built_in {
  font-weight: normal;
}

pre .xml .css,
pre .xml .javascript,
pre .xml .vbscript,
pre .tex .formula {
  opacity: 0.5;
}pre code {
  display: block; padding: 0.5em;
  background: #F0F0F0;
}

pre code,
pre .ruby .subst,
pre .tag .title,
pre .lisp .title {
  color: black;
}

pre .string,
pre .title,
pre .constant,
pre .parent,
pre .tag .value,
pre .rules .value,
pre .rules .value .number,
pre .preprocessor,
pre .ruby .symbol,
pre .ruby .symbol .string,
pre .ruby .symbol .keyword,
pre .ruby .symbol .keymethods,
pre .instancevar,
pre .aggregate,
pre .template_tag,
pre .django .variable,
pre .smalltalk .class,
pre .addition,
pre .flow,
pre .stream,
pre .bash .variable,
pre .apache .tag,
pre .apache .cbracket,
pre .tex .command,
pre .tex .special,
pre .erlang_repl .function_or_atom {
  color: #800;
}

pre .comment,
pre .annotation,
pre .template_comment,
pre .diff .header,
pre .chunk {
  color: #888;
}

pre .number,
pre .date,
pre .regexp,
pre .literal,
pre .smalltalk .symbol,
pre .smalltalk .char,
pre .go .constant,
pre .change {
  color: #080;
}

pre .label,
pre .javadoc,
pre .ruby .string,
pre .decorator,
pre .filter .argument,
pre .localvars,
pre .array,
pre .attr_selector,
pre .important,
pre .pseudo,
pre .pi,
pre .doctype,
pre .deletion,
pre .envvar,
pre .shebang,
pre .apache .sqbracket,
pre .nginx .built_in,
pre .tex .formula,
pre .erlang_repl .reserved,
pre .input_number {
  color: #88F
}

pre .css .tag,
pre .javadoctag,
pre .phpdoc,
pre .yardoctag {
  font-weight: bold;
}

pre .keyword,
pre .id,
pre .phpdoc,
pre .title,
pre .built_in,
pre .aggregate,
pre .smalltalk .class,
pre .winutils,
pre .bash .variable,
pre .apache .tag,
pre .go .typename,
pre .tex .command {
  font-weight: bold;
}

pre .nginx .built_in {
  font-weight: normal;
}

pre .xml .css,
pre .xml .javascript,
pre .xml .vbscript,
pre .tex .formula {
  opacity: 0.5;
}pre code {
  display: block; padding: 0.5em;
  background: #F0F0F0;
}

pre code,
pre .ruby .subst,
pre .tag .title,
pre .lisp .title {
  color: black;
}

pre .string,
pre .title,
pre .constant,
pre .parent,
pre .tag .value,
pre .rules .value,
pre .rules .value .number,
pre .preprocessor,
pre .ruby .symbol,
pre .ruby .symbol .string,
pre .ruby .symbol .keyword,
pre .ruby .symbol .keymethods,
pre .instancevar,
pre .aggregate,
pre .template_tag,
pre .django .variable,
pre .smalltalk .class,
pre .addition,
pre .flow,
pre .stream,
pre .bash .variable,
pre .apache .tag,
pre .apache .cbracket,
pre .tex .command,
pre .tex .special,
pre .erlang_repl .function_or_atom {
  color: #800;
}

pre .comment,
pre .annotation,
pre .template_comment,
pre .diff .header,
pre .chunk {
  color: #888;
}

pre .number,
pre .date,
pre .regexp,
pre .literal,
pre .smalltalk .symbol,
pre .smalltalk .char,
pre .go .constant,
pre .change {
  color: #080;
}

pre .label,
pre .javadoc,
pre .ruby .string,
pre .decorator,
pre .filter .argument,
pre .localvars,
pre .array,
pre .attr_selector,
pre .important,
pre .pseudo,
pre .pi,
pre .doctype,
pre .deletion,
pre .envvar,
pre .shebang,
pre .apache .sqbracket,
pre .nginx .built_in,
pre .tex .formula,
pre .erlang_repl .reserved,
pre .input_number {
  color: #88F
}

pre .css .tag,
pre .javadoctag,
pre .phpdoc,
pre .yardoctag {
  font-weight: bold;
}

pre .keyword,
pre .id,
pre .phpdoc,
pre .title,
pre .built_in,
pre .aggregate,
pre .smalltalk .class,
pre .winutils,
pre .bash .variable,
pre .apache .tag,
pre .go .typename,
pre .tex .command {
  font-weight: bold;
}

pre .nginx .built_in {
  font-weight: normal;
}

pre .xml .css,
pre .xml .javascript,
pre .xml .vbscript,
pre .tex .formula {
  opacity: 0.5;
}pre code {
  display: block; padding: 0.5em;
  background: #F0F0F0;
}

pre code,
pre .ruby .subst,
pre .tag .title,
pre .lisp .title {
  color: black;
}

pre .string,
pre .title,
pre .constant,
pre .parent,
pre .tag .value,
pre .rules .value,
pre .rules .value .number,
pre .preprocessor,
pre .ruby .symbol,
pre .ruby .symbol .string,
pre .ruby .symbol .keyword,
pre .ruby .symbol .keymethods,
pre .instancevar,
pre .aggregate,
pre .template_tag,
pre .django .variable,
pre .smalltalk .class,
pre .addition,
pre .flow,
pre .stream,
pre .bash .variable,
pre .apache .tag,
pre .apache .cbracket,
pre .tex .command,
pre .tex .special,
pre .erlang_repl .function_or_atom {
  color: #800;
}

pre .comment,
pre .annotation,
pre .template_comment,
pre .diff .header,
pre .chunk {
  color: #888;
}

pre .number,
pre .date,
pre .regexp,
pre .literal,
pre .smalltalk .symbol,
pre .smalltalk .char,
pre .go .constant,
pre .change {
  color: #080;
}

pre .label,
pre .javadoc,
pre .ruby .string,
pre .decorator,
pre .filter .argument,
pre .localvars,
pre .array,
pre .attr_selector,
pre .important,
pre .pseudo,
pre .pi,
pre .doctype,
pre .deletion,
pre .envvar,
pre .shebang,
pre .apache .sqbracket,
pre .nginx .built_in,
pre .tex .formula,
pre .erlang_repl .reserved,
pre .input_number {
  color: #88F
}

pre .css .tag,
pre .javadoctag,
pre .phpdoc,
pre .yardoctag {
  font-weight: bold;
}

pre .keyword,
pre .id,
pre .phpdoc,
pre .title,
pre .built_in,
pre .aggregate,
pre .smalltalk .class,
pre .winutils,
pre .bash .variable,
pre .apache .tag,
pre .go .typename,
pre .tex .command {
  font-weight: bold;
}

pre .nginx .built_in {
  font-weight: normal;
}

pre .xml .css,
pre .xml .javascript,
pre .xml .vbscript,
pre .tex .formula {
  opacity: 0.5;
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


  </style>
  <script type="text/javascript">
      SyntaxHighlighter.defaults['gutter'] = false;
      SyntaxHighlighter.defaults['toolbar'] = false;
      SyntaxHighlighter.all()
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

    <h2>WSGI Environment</h2>
    <div id="environ">
      <pre class="brush: python">${environment}</pre>
    </div>
  </div>
 </body>
</html>
'''

debug_template = Template(debug_template_raw)


class DebugMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        assert not environ['wsgi.multiprocess'], (
            "The DebugMiddleware middleware is not usable in a "
            "multi-process environment")
        try:
            return self.app(environ, start_response)
        except:
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
                shthemedefault=shthemedefault
            )

            # construct and return our response
            response = Response()
            response.status_int = 400
            response.unicode_body = result
            return response(environ, start_response)

pecan_image = "data:image/png;base64,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%3D"  # noqa

shcore = "data:application/x-javascript;base64,LyoqCiAqIFN5bnRheEhpZ2hsaWdodGVyCiAqIGh0dHA6Ly9hbGV4Z29yYmF0Y2hldi5jb20vU3ludGF4SGlnaGxpZ2h0ZXIKICoKICogU3ludGF4SGlnaGxpZ2h0ZXIgaXMgZG9uYXRpb253YXJlLiBJZiB5b3UgYXJlIHVzaW5nIGl0LCBwbGVhc2UgZG9uYXRlLgogKiBodHRwOi8vYWxleGdvcmJhdGNoZXYuY29tL1N5bnRheEhpZ2hsaWdodGVyL2RvbmF0ZS5odG1sCiAqCiAqIEB2ZXJzaW9uCiAqIDMuMC44MyAoSnVseSAwMiAyMDEwKQogKiAKICogQGNvcHlyaWdodAogKiBDb3B5cmlnaHQgKEMpIDIwMDQtMjAxMCBBbGV4IEdvcmJhdGNoZXYuCiAqCiAqIEBsaWNlbnNlCiAqIER1YWwgbGljZW5zZWQgdW5kZXIgdGhlIE1JVCBhbmQgR1BMIGxpY2Vuc2VzLgogKi8KZXZhbChmdW5jdGlvbihwLGEsYyxrLGUsZCl7ZT1mdW5jdGlvbihjKXtyZXR1cm4oYzxhPycnOmUocGFyc2VJbnQoYy9hKSkpKygoYz1jJWEpPjM1P1N0cmluZy5mcm9tQ2hhckNvZGUoYysyOSk6Yy50b1N0cmluZygzNikpfTtpZighJycucmVwbGFjZSgvXi8sU3RyaW5nKSl7d2hpbGUoYy0tKXtkW2UoYyldPWtbY118fGUoYyl9az1bZnVuY3Rpb24oZSl7cmV0dXJuIGRbZV19XTtlPWZ1bmN0aW9uKCl7cmV0dXJuJ1xcdysnfTtjPTF9O3doaWxlKGMtLSl7aWYoa1tjXSl7cD1wLnJlcGxhY2UobmV3IFJlZ0V4cCgnXFxiJytlKGMpKydcXGInLCdnJyksa1tjXSl9fXJldHVybiBwfSgnSyBNO0koTSkxUyAyVSgiMmFcJ3QgNGsgTSA0SyAyZyAzbCA0RyA0SCIpOyg2KCl7NiByKGYsZSl7SSghTS4xUihmKSkxUyAzbSgiM3MgMTUgNFIiKTtLIGE9Zi4xdztmPU0oZi4xbSx0KGYpKyhlfHwiIikpO0koYSlmLjF3PXsxbTphLjFtLDE5OmEuMTk/YS4xOS4xYSgwKTpOfTtIIGZ9NiB0KGYpe0goZi4xSj8iZyI6IiIpKyhmLjRzPyJpIjoiIikrKGYuNHA/Im0iOiIiKSsoZi40dj8ieCI6IiIpKyhmLjNuPyJ5IjoiIil9NiBCKGYsZSxhLGIpe0sgYz11LkwsZCxoLGc7dj1SOzVLe08oO2MtLTspe2c9dVtjXTtJKGEmZy4zciYmKCFnLjJwfHxnLjJwLlcoYikpKXtnLjJxLjEyPWU7SSgoaD1nLjJxLlgoZikpJiZoLlA9PT1lKXtkPXszazpnLjJiLlcoYixoLGEpLDFDOmh9OzFOfX19fTV2KGkpezFTIGl9NXF7dj0xMX1IIGR9NiBwKGYsZSxhKXtJKDNiLlouMWkpSCBmLjFpKGUsYSk7TyhhPWF8fDA7YTxmLkw7YSsrKUkoZlthXT09PWUpSCBhO0gtMX1NPTYoZixlKXtLIGE9W10sYj1NLjFCLGM9MCxkLGg7SShNLjFSKGYpKXtJKGUhPT0xZCkxUyAzbSgiMmFcJ3QgNXIgNUkgNUYgNUIgNUMgMTUgNUUgNXAiKTtIIHIoZil9SSh2KTFTIDJVKCIyYVwndCBXIDNsIE0gNTkgNW0gNWcgNXggNWkiKTtlPWV8fCIiO08oZD17Mk46MTEsMTk6W10sMks6NihnKXtIIGUuMWkoZyk+LTF9LDNkOjYoZyl7ZSs9Z319O2M8Zi5MOylJKGg9QihmLGMsYixkKSl7YS5VKGguM2spO2MrPWguMUNbMF0uTHx8MX1ZIEkoaD1uLlguVyh6W2JdLGYuMWEoYykpKXthLlUoaFswXSk7Yys9aFswXS5MfVl7aD1mLjNhKGMpO0koaD09PSJbIiliPU0uMkk7WSBJKGg9PT0iXSIpYj1NLjFCO2EuVShoKTtjKyt9YT0xNShhLjFLKCIiKSxuLlEuVyhlLHcsIiIpKTthLjF3PXsxbTpmLDE5OmQuMk4/ZC4xOTpOfTtIIGF9O00uM3Y9IjEuNS4wIjtNLjJJPTE7TS4xQj0yO0sgQz0vXFwkKD86KFxcZFxcZD98WyQmYFwnXSl8eyhbJFxcd10rKX0pL2csdz0vW141aF0rfChbXFxzXFxTXSkoPz1bXFxzXFxTXSpcXDEpL2csQT0vXig/Ols/KitdfHtcXGQrKD86LFxcZCopP30pXFw/Py8sdj0xMSx1PVtdLG49e1g6MTUuWi5YLDFBOjE1LlouMUEsMUM6MXIuWi4xQyxROjFyLlouUSwxZToxci5aLjFlfSx4PW4uWC5XKC8oKT8/LywiIilbMV09PT0xZCxEPTYoKXtLIGY9L14vZztuLjFBLlcoZiwiIik7SCFmLjEyfSgpLHk9Nigpe0sgZj0veC9nO24uUS5XKCJ4IixmLCIiKTtIIWYuMTJ9KCksRT0xNS5aLjNuIT09MWQsej17fTt6W00uMkldPS9eKD86XFxcXCg/OlswLTNdWzAtN117MCwyfXxbNC03XVswLTddP3x4W1xcMjktMjYtZl17Mn18dVtcXDI5LTI2LWZdezR9fGNbQS0zby16XXxbXFxzXFxTXSkpLzt6W00uMUJdPS9eKD86XFxcXCg/OjAoPzpbMC0zXVswLTddezAsMn18WzQtN11bMC03XT8pP3xbMS05XVxcZCp8eFtcXDI5LTI2LWZdezJ9fHVbXFwyOS0yNi1mXXs0fXxjW0EtM28tel18W1xcc1xcU10pfFxcKFxcP1s6PSFdfFs/KitdXFw/fHtcXGQrKD86LFxcZCopP31cXD8/KS87TS4xaD02KGYsZSxhLGIpe3UuVSh7MnE6cihmLCJnIisoRT8ieSI6IiIpKSwyYjplLDNyOmF8fE0uMUIsMnA6Ynx8Tn0pfTtNLjJuPTYoZixlKXtLIGE9ZisiLyIrKGV8fCIiKTtIIE0uMm5bYV18fChNLjJuW2FdPU0oZixlKSl9O00uM2M9NihmKXtIIHIoZiwiZyIpfTtNLjVsPTYoZil7SCBmLlEoL1stW1xcXXt9KCkqKz8uLFxcXFxeJHwjXFxzXS9nLCJcXFxcJCYiKX07TS41ZT02KGYsZSxhLGIpe2U9cihlLCJnIisoYiYmRT8ieSI6IiIpKTtlLjEyPWE9YXx8MDtmPWUuWChmKTtIIGI/ZiYmZi5QPT09YT9mOk46Zn07TS4zcT02KCl7TS4xaD02KCl7MVMgMlUoIjJhXCd0IDU1IDFoIDU0IDNxIil9fTtNLjFSPTYoZil7SCA1My5aLjFxLlcoZik9PT0iWzJtIDE1XSJ9O00uM3A9NihmLGUsYSxiKXtPKEsgYz1yKGUsImciKSxkPS0xLGg7aD1jLlgoZik7KXthLlcoYixoLCsrZCxmLGMpO2MuMTI9PT1oLlAmJmMuMTIrK31JKGUuMUopZS4xMj0wfTtNLjU3PTYoZixlKXtIIDYgYShiLGMpe0sgZD1lW2NdLjFJP2VbY106ezFJOmVbY119LGg9cihkLjFJLCJnIiksZz1bXSxpO08oaT0wO2k8Yi5MO2krKylNLjNwKGJbaV0saCw2KGspe2cuVShkLjNqP2tbZC4zal18fCIiOmtbMF0pfSk7SCBjPT09ZS5MLTF8fCFnLkw/ZzphKGcsYysxKX0oW2ZdLDApfTsxNS5aLjFwPTYoZixlKXtIIEouWChlWzBdKX07MTUuWi5XPTYoZixlKXtIIEouWChlKX07MTUuWi5YPTYoZil7SyBlPW4uWC4xcChKLDE0KSxhO0koZSl7SSgheCYmZS5MPjEmJnAoZSwiIik+LTEpe2E9MTUoSi4xbSxuLlEuVyh0KEopLCJnIiwiIikpO24uUS5XKGYuMWEoZS5QKSxhLDYoKXtPKEsgYz0xO2M8MTQuTC0yO2MrKylJKDE0W2NdPT09MWQpZVtjXT0xZH0pfUkoSi4xdyYmSi4xdy4xOSlPKEsgYj0xO2I8ZS5MO2IrKylJKGE9Si4xdy4xOVtiLTFdKWVbYV09ZVtiXTshRCYmSi4xSiYmIWVbMF0uTCYmSi4xMj5lLlAmJkouMTItLX1IIGV9O0koIUQpMTUuWi4xQT02KGYpeyhmPW4uWC5XKEosZikpJiZKLjFKJiYhZlswXS5MJiZKLjEyPmYuUCYmSi4xMi0tO0ghIWZ9OzFyLlouMUM9NihmKXtNLjFSKGYpfHwoZj0xNShmKSk7SShmLjFKKXtLIGU9bi4xQy4xcChKLDE0KTtmLjEyPTA7SCBlfUggZi5YKEopfTsxci5aLlE9NihmLGUpe0sgYT1NLjFSKGYpLGIsYztJKGEmJjFqIGUuNTgoKT09PSIzZiImJmUuMWkoIiR7Iik9PT0tMSYmeSlIIG4uUS4xcChKLDE0KTtJKGEpe0koZi4xdyliPWYuMXcuMTl9WSBmKz0iIjtJKDFqIGU9PT0iNiIpYz1uLlEuVyhKLGYsNigpe0koYil7MTRbMF09MWYgMXIoMTRbMF0pO08oSyBkPTA7ZDxiLkw7ZCsrKUkoYltkXSkxNFswXVtiW2RdXT0xNFtkKzFdfUkoYSYmZi4xSilmLjEyPTE0WzE0LkwtMl0rMTRbMF0uTDtIIGUuMXAoTiwxNCl9KTtZe2M9SisiIjtjPW4uUS5XKGMsZiw2KCl7SyBkPTE0O0ggbi5RLlcoZSxDLDYoaCxnLGkpe0koZyk1YihnKXsyNCIkIjpIIiQiOzI0IiYiOkggZFswXTsyNCJgIjpIIGRbZC5MLTFdLjFhKDAsZFtkLkwtMl0pOzI0IlwnIjpIIGRbZC5MLTFdLjFhKGRbZC5MLTJdK2RbMF0uTCk7NWE6aT0iIjtnPStnO0koIWcpSCBoO08oO2c+ZC5MLTM7KXtpPTFyLlouMWEuVyhnLC0xKStpO2c9MVEuM2koZy8xMCl9SChnP2RbZ118fCIiOiIkIikraX1Ze2c9K2k7SShnPD1kLkwtMylIIGRbZ107Zz1iP3AoYixpKTotMTtIIGc+LTE/ZFtnKzFdOmh9fSl9KX1JKGEmJmYuMUopZi4xMj0wO0ggY307MXIuWi4xZT02KGYsZSl7SSghTS4xUihmKSlIIG4uMWUuMXAoSiwxNCk7SyBhPUorIiIsYj1bXSxjPTAsZCxoO0koZT09PTFkfHwrZTwwKWU9NUQ7WXtlPTFRLjNpKCtlKTtJKCFlKUhbXX1PKGY9TS4zYyhmKTtkPWYuWChhKTspe0koZi4xMj5jKXtiLlUoYS4xYShjLGQuUCkpO2QuTD4xJiZkLlA8YS5MJiYzYi5aLlUuMXAoYixkLjFhKDEpKTtoPWRbMF0uTDtjPWYuMTI7SShiLkw+PWUpMU59Zi4xMj09PWQuUCYmZi4xMisrfUkoYz09PWEuTCl7SSghbi4xQS5XKGYsIiIpfHxoKWIuVSgiIil9WSBiLlUoYS4xYShjKSk7SCBiLkw+ZT9iLjFhKDAsZSk6Yn07TS4xaCgvXFwoXFw/I1teKV0qXFwpLyw2KGYpe0ggbi4xQS5XKEEsZi4yUy4xYShmLlArZlswXS5MKSk/IiI6Iig/OikifSk7TS4xaCgvXFwoKD8hXFw/KS8sNigpe0ouMTkuVShOKTtIIigifSk7TS4xaCgvXFwoXFw/PChbJFxcd10rKT4vLDYoZil7Si4xOS5VKGZbMV0pO0ouMk49UjtIIigifSk7TS4xaCgvXFxcXGs8KFtcXHckXSspPi8sNihmKXtLIGU9cChKLjE5LGZbMV0pO0ggZT4tMT8iXFxcXCIrKGUrMSkrKDNSKGYuMlMuM2EoZi5QK2ZbMF0uTCkpPyIiOiIoPzopIik6ZlswXX0pO00uMWgoL1xcW1xcXj9dLyw2KGYpe0ggZlswXT09PSJbXSI/IlxcXFxiXFxcXEIiOiJbXFxcXHNcXFxcU10ifSk7TS4xaCgvXlxcKFxcPyhbNUFdKylcXCkvLDYoZil7Si4zZChmWzFdKTtIIiJ9KTtNLjFoKC8oPzpcXHMrfCMuKikrLyw2KGYpe0ggbi4xQS5XKEEsZi4yUy4xYShmLlArZlswXS5MKSk/IiI6Iig/OikifSxNLjFCLDYoKXtIIEouMksoIngiKX0pO00uMWgoL1xcLi8sNigpe0giW1xcXFxzXFxcXFNdIn0sTS4xQiw2KCl7SCBKLjJLKCJzIil9KX0pKCk7MWogMmUhPSIxZCImJigyZS5NPU0pO0sgMXY9NigpezYgcihhLGIpe2EuMWwuMWkoYikhPS0xfHwoYS4xbCs9IiAiK2IpfTYgdChhKXtIIGEuMWkoIjNlIik9PTA/YToiM2UiK2F9NiBCKGEpe0ggZS4xWS4yQVt0KGEpXX02IHAoYSxiLGMpe0koYT09TilIIE47SyBkPWMhPVI/YS4zRzpbYS4yR10saD17IiMiOiIxYyIsIi4iOiIxbCJ9W2IuMW8oMCwxKV18fCIzaCIsZyxpO2c9aCE9IjNoIj9iLjFvKDEpOmIuNXUoKTtJKChhW2hdfHwiIikuMWkoZykhPS0xKUggYTtPKGE9MDtkJiZhPGQuTCYmaT09TjthKyspaT1wKGRbYV0sYixjKTtIIGl9NiBDKGEsYil7SyBjPXt9LGQ7TyhkIDJnIGEpY1tkXT1hW2RdO08oZCAyZyBiKWNbZF09YltkXTtIIGN9NiB3KGEsYixjLGQpezYgaChnKXtnPWd8fDFQLjV5O0koIWcuMUYpe2cuMUY9Zy41MjtnLjNOPTYoKXtKLjV3PTExfX1jLlcoZHx8MVAsZyl9YS4zZz9hLjNnKCI0VSIrYixoKTphLjR5KGIsaCwxMSl9NiBBKGEsYil7SyBjPWUuMVkuMmosZD1OO0koYz09Til7Yz17fTtPKEsgaCAyZyBlLjFVKXtLIGc9ZS4xVVtoXTtkPWcuNHg7SShkIT1OKXtnLjFWPWguNHcoKTtPKGc9MDtnPGQuTDtnKyspY1tkW2ddXT1ofX1lLjFZLjJqPWN9ZD1lLjFVW2NbYV1dO2Q9PU4mJmIhPTExJiYxUC4xWChlLjEzLjF4LjFYKyhlLjEzLjF4LjNFK2EpKTtIIGR9NiB2KGEsYil7TyhLIGM9YS4xZSgiXFxuIiksZD0wO2Q8Yy5MO2QrKyljW2RdPWIoY1tkXSxkKTtIIGMuMUsoIlxcbiIpfTYgdShhLGIpe0koYT09Tnx8YS5MPT0wfHxhPT0iXFxuIilIIGE7YT1hLlEoLzwvZywiJjF5OyIpO2E9YS5RKC8gezIsfS9nLDYoYyl7TyhLIGQ9IiIsaD0wO2g8Yy5MLTE7aCsrKWQrPWUuMTMuMVc7SCBkKyIgIn0pO0koYiE9TilhPXYoYSw2KGMpe0koYy5MPT0wKUgiIjtLIGQ9IiI7Yz1jLlEoL14oJjJzO3wgKSsvLDYoaCl7ZD1oO0giIn0pO0koYy5MPT0wKUggZDtIIGQrXCc8MTcgMWc9IlwnK2IrXCciPlwnK2MrIjwvMTc+In0pO0ggYX02IG4oYSxiKXthLjFlKCJcXG4iKTtPKEsgYz0iIixkPTA7ZDw1MDtkKyspYys9IiAgICAgICAgICAgICAgICAgICAgIjtIIGE9dihhLDYoaCl7SShoLjFpKCJcXHQiKT09LTEpSCBoO08oSyBnPTA7KGc9aC4xaSgiXFx0IikpIT0tMTspaD1oLjFvKDAsZykrYy4xbygwLGItZyViKStoLjFvKGcrMSxoLkwpO0ggaH0pfTYgeChhKXtIIGEuUSgvXlxccyt8XFxzKyQvZywiIil9NiBEKGEsYil7SShhLlA8Yi5QKUgtMTtZIEkoYS5QPmIuUClIIDE7WSBJKGEuTDxiLkwpSC0xO1kgSShhLkw+Yi5MKUggMTtIIDB9NiB5KGEsYil7NiBjKGspe0gga1swXX1PKEsgZD1OLGg9W10sZz1iLjJEP2IuMkQ6YzsoZD1iLjFJLlgoYSkpIT1OOyl7SyBpPWcoZCxiKTtJKDFqIGk9PSIzZiIpaT1bMWYgZS4yTChpLGQuUCxiLjIzKV07aD1oLjFPKGkpfUggaH02IEUoYSl7SyBiPS8oLiopKCgmMUc7fCYxeTspLiopLztIIGEuUShlLjNBLjNNLDYoYyl7SyBkPSIiLGg9TjtJKGg9Yi5YKGMpKXtjPWhbMV07ZD1oWzJdfUhcJzxhIDJoPSJcJytjK1wnIj5cJytjKyI8L2E+IitkfSl9NiB6KCl7TyhLIGE9MUUuMzYoIjFrIiksYj1bXSxjPTA7YzxhLkw7YysrKWFbY10uM3M9PSIyMCImJmIuVShhW2NdKTtIIGJ9NiBmKGEpe2E9YS4xRjtLIGI9cChhLCIuMjAiLFIpO2E9cChhLCIuM08iLFIpO0sgYz0xRS40aSgiM3QiKTtJKCEoIWF8fCFifHxwKGEsIjN0IikpKXtCKGIuMWMpO3IoYiwiMW0iKTtPKEsgZD1hLjNHLGg9W10sZz0wO2c8ZC5MO2crKyloLlUoZFtnXS40enx8ZFtnXS40QSk7aD1oLjFLKCJcXHIiKTtjLjM5KDFFLjREKGgpKTthLjM5KGMpO2MuMkMoKTtjLjRDKCk7dyhjLCI0dSIsNigpe2MuMkcuNEUoYyk7Yi4xbD1iLjFsLlEoIjFtIiwiIil9KX19SSgxaiAzRiE9IjFkIiYmMWogTT09IjFkIilNPTNGKCJNIikuTTtLIGU9ezJ2OnsiMWctMjciOiIiLCIyaS0xcyI6MSwiMnotMXMtMnQiOjExLDFNOk4sMXQ6TiwiNDItNDUiOlIsIjQzLTIyIjo0LDF1OlIsMTY6UiwiM1YtMTciOlIsMmw6MTEsIjQxLTQwIjpSLDJrOjExLCIxei0xayI6MTF9LDEzOnsxVzoiJjJzOyIsMk06Uiw0NjoxMSw0NDoxMSwzNDoiNG4iLDF4OnsyMToiNG8gMW0iLDJQOiI/IiwxWDoiMXZcXG5cXG4iLDNFOiI0clwndCA0dCAxRCBPOiAiLDRnOiI0bSA0QlwndCA1MSBPIDF6LTFrIDRGOiAiLDM3OlwnPCE0VCAxeiA0UyAiLS8vNFYvLzNIIDRXIDEuMCA0Wi8vNFkiICIxWjovLzJ5LjNMLjNLLzRYLzNJLzNILzNJLTRQLjRKIj48MXogNEk9IjFaOi8vMnkuM0wuM0svNEwvNUwiPjwzSj48NE4gMVotNE09IjVHLTVNIiA2Sz0iMk8vMXo7IDZKPTZJLTgiIC8+PDF0PjZMIDF2PC8xdD48LzNKPjwzQiAxTD0iMjUtNk06NlEsNlAsNk8sNk4tNkY7NnktMmY6IzZ4OzJmOiM2dzsyNS0yMjo2djsyTy0zRDozQzsiPjxUIDFMPSIyTy0zRDozQzszdy0zMjoxLjZ6OyI+PFQgMUw9IjI1LTIyOjZBLTZFOyI+MXY8L1Q+PFQgMUw9IjI1LTIyOi42Qzszdy02Qjo2UjsiPjxUPjN2IDMuMC43NiAoNzIgNzMgM3gpPC9UPjxUPjxhIDJoPSIxWjovLzN1LjJ3LzF2IiAxRj0iMzgiIDFMPSIyZjojM3kiPjFaOi8vM3UuMncvMXY8L2E+PC9UPjxUPjcwIDE3IDZVIDcxLjwvVD48VD42VCA2WC0zeCA2WSA2RC48L1Q+PC9UPjxUPjZ0IDYxIDYwIEogMWssIDVaIDxhIDJoPSI2dTovLzJ5LjYyLjJ3LzYzLTY2LzY1PzY0PTVYLTVXJjVQPTVPIiAxTD0iMmY6IzN5Ij41UjwvYT4gNVYgPDJSLz41VSA1VCA1UyE8L1Q+PC9UPjwvM0I+PC8xej5cJ319LDFZOnsyajpOLDJBOnt9fSwxVTp7fSwzQTp7Nm46L1xcL1xcKltcXHNcXFNdKj9cXCpcXC8vMmMsNm06L1xcL1xcLy4qJC8yYyw2bDovIy4qJC8yYyw2azovIihbXlxcXFwiXFxuXXxcXFxcLikqIi9nLDZvOi9cJyhbXlxcXFxcJ1xcbl18XFxcXC4pKlwnL2csNnA6MWYgTShcJyIoW15cXFxcXFxcXCJdfFxcXFxcXFxcLikqIlwnLCIzeiIpLDZzOjFmIE0oIlwnKFteXFxcXFxcXFxcJ118XFxcXFxcXFwuKSpcJyIsIjN6IiksNnE6LygmMXk7fDwpIS0tW1xcc1xcU10qPy0tKCYxRzt8PikvMmMsM006L1xcdys6XFwvXFwvW1xcdy0uXFwvPyUmPTpAO10qL2csNmE6ezE4Oi8oJjF5O3w8KVxcPz0/L2csMWI6L1xcPygmMUc7fD4pL2d9LDY5OnsxODovKCYxeTt8PCklPT8vZywxYjovJSgmMUc7fD4pL2d9LDZkOnsxODovKCYxeTt8PClcXHMqMWsuKj8oJjFHO3w+KS8yVCwxYjovKCYxeTt8PClcXC9cXHMqMWtcXHMqKCYxRzt8PikvMlR9fSwxNjp7MUg6NihhKXs2IGIoaSxrKXtIIGUuMTYuMm8oaSxrLGUuMTMuMXhba10pfU8oSyBjPVwnPFQgMWc9IjE2Ij5cJyxkPWUuMTYuMngsaD1kLjJYLGc9MDtnPGguTDtnKyspYys9KGRbaFtnXV0uMUh8fGIpKGEsaFtnXSk7Yys9IjwvVD4iO0ggY30sMm86NihhLGIsYyl7SFwnPDJXPjxhIDJoPSIjIiAxZz0iNmUgNmhcJytiKyIgIitiK1wnIj5cJytjKyI8L2E+PC8yVz4ifSwyYjo2KGEpe0sgYj1hLjFGLGM9Yi4xbHx8IiI7Yj1CKHAoYiwiLjIwIixSKS4xYyk7SyBkPTYoaCl7SChoPTE1KGgrIjZmKFxcXFx3KykiKS5YKGMpKT9oWzFdOk59KCI2ZyIpO2ImJmQmJmUuMTYuMnhbZF0uMkIoYik7YS4zTigpfSwyeDp7Mlg6WyIyMSIsIjJQIl0sMjE6ezFIOjYoYSl7SShhLlYoIjJsIikhPVIpSCIiO0sgYj1hLlYoIjF0Iik7SCBlLjE2LjJvKGEsIjIxIixiP2I6ZS4xMy4xeC4yMSl9LDJCOjYoYSl7YT0xRS42aih0KGEuMWMpKTthLjFsPWEuMWwuUSgiNDciLCIiKX19LDJQOnsyQjo2KCl7SyBhPSI2OD0wIjthKz0iLCAxOD0iKygzMS4zMC0zMykvMisiLCAzMj0iKygzMS4yWi0yWSkvMisiLCAzMD0zMywgMlo9MlkiO2E9YS5RKC9eLC8sIiIpO2E9MVAuNlooIiIsIjM4IixhKTthLjJDKCk7SyBiPWEuMUU7Yi42VyhlLjEzLjF4LjM3KTtiLjZWKCk7YS4yQygpfX19fSwzNTo2KGEsYil7SyBjO0koYiljPVtiXTtZe2M9MUUuMzYoZS4xMy4zNCk7TyhLIGQ9W10saD0wO2g8Yy5MO2grKylkLlUoY1toXSk7Yz1kfWM9YztkPVtdO0koZS4xMy4yTSljPWMuMU8oeigpKTtJKGMuTD09PTApSCBkO08oaD0wO2g8Yy5MO2grKyl7TyhLIGc9Y1toXSxpPWEsaz1jW2hdLjFsLGo9M1cgMCxsPXt9LG09MWYgTSgiXlxcXFxbKD88MlY+KC4qPykpXFxcXF0kIikscz0xZiBNKCIoPzwyNz5bXFxcXHctXSspXFxcXHMqOlxcXFxzKig/PDFUPltcXFxcdy0lI10rfFxcXFxbLio/XFxcXF18XFwiLio/XFwifFwnLio/XCcpXFxcXHMqOz8iLCJnIik7KGo9cy5YKGspKSE9Tjspe0sgbz1qLjFULlEoL15bXCciXXxbXCciXSQvZywiIik7SShvIT1OJiZtLjFBKG8pKXtvPW0uWChvKTtvPW8uMlYuTD4wP28uMlYuMWUoL1xccyosXFxzKi8pOltdfWxbai4yN109b31nPXsxRjpnLDFuOkMoaSxsKX07Zy4xbi4xRCE9TiYmZC5VKGcpfUggZH0sMU06NihhLGIpe0sgYz1KLjM1KGEsYiksZD1OLGg9ZS4xMztJKGMuTCE9PTApTyhLIGc9MDtnPGMuTDtnKyspe2I9Y1tnXTtLIGk9Yi4xRixrPWIuMW4saj1rLjFELGw7SShqIT1OKXtJKGtbIjF6LTFrIl09PSJSInx8ZS4ydlsiMXotMWsiXT09Uil7ZD0xZiBlLjRsKGopO2o9IjRPIn1ZIEkoZD1BKGopKWQ9MWYgZDtZIDZIO2w9aS4zWDtJKGguMk0pe2w9bDtLIG09eChsKSxzPTExO0kobS4xaSgiPCFbNkdbIik9PTApe209bS40aCg5KTtzPVJ9SyBvPW0uTDtJKG0uMWkoIl1dXFw+Iik9PW8tMyl7bT1tLjRoKDAsby0zKTtzPVJ9bD1zP206bH1JKChpLjF0fHwiIikhPSIiKWsuMXQ9aS4xdDtrLjFEPWo7ZC4yUShrKTtiPWQuMkYobCk7SSgoaS4xY3x8IiIpIT0iIiliLjFjPWkuMWM7aS4yRy43NChiLGkpfX19LDJFOjYoYSl7dygxUCwiNGsiLDYoKXtlLjFNKGEpfSl9fTtlLjJFPWUuMkU7ZS4xTT1lLjFNO2UuMkw9NihhLGIsYyl7Si4xVD1hO0ouUD1iO0ouTD1hLkw7Si4yMz1jO0ouMVY9Tn07ZS4yTC5aLjFxPTYoKXtIIEouMVR9O2UuNGw9NihhKXs2IGIoaixsKXtPKEsgbT0wO208ai5MO20rKylqW21dLlArPWx9SyBjPUEoYSksZCxoPTFmIGUuMVUuNVksZz1KLGk9IjJGIDFIIDJRIi4xZSgiICIpO0koYyE9Til7ZD0xZiBjO08oSyBrPTA7azxpLkw7aysrKSg2KCl7SyBqPWlba107Z1tqXT02KCl7SCBoW2pdLjFwKGgsMTQpfX0pKCk7ZC4yOD09Tj8xUC4xWChlLjEzLjF4LjFYKyhlLjEzLjF4LjRnK2EpKTpoLjJKLlUoezFJOmQuMjguMTcsMkQ6NihqKXtPKEsgbD1qLjE3LG09W10scz1kLjJKLG89ai5QK2ouMTguTCxGPWQuMjgscSxHPTA7RzxzLkw7RysrKXtxPXkobCxzW0ddKTtiKHEsbyk7bT1tLjFPKHEpfUkoRi4xOCE9TiYmai4xOCE9Til7cT15KGouMTgsRi4xOCk7YihxLGouUCk7bT1tLjFPKHEpfUkoRi4xYiE9TiYmai4xYiE9Til7cT15KGouMWIsRi4xYik7YihxLGouUCtqWzBdLjVRKGouMWIpKTttPW0uMU8ocSl9TyhqPTA7ajxtLkw7aisrKW1bal0uMVY9Yy4xVjtIIG19fSl9fTtlLjRqPTYoKXt9O2UuNGouWj17Vjo2KGEsYil7SyBjPUouMW5bYV07Yz1jPT1OP2I6YztLIGQ9eyJSIjpSLCIxMSI6MTF9W2NdO0ggZD09Tj9jOmR9LDNZOjYoYSl7SCAxRS40aShhKX0sNGM6NihhLGIpe0sgYz1bXTtJKGEhPU4pTyhLIGQ9MDtkPGEuTDtkKyspSSgxaiBhW2RdPT0iMm0iKWM9Yy4xTyh5KGIsYVtkXSkpO0ggSi40ZShjLjZiKEQpKX0sNGU6NihhKXtPKEsgYj0wO2I8YS5MO2IrKylJKGFbYl0hPT1OKU8oSyBjPWFbYl0sZD1jLlArYy5MLGg9YisxO2g8YS5MJiZhW2JdIT09TjtoKyspe0sgZz1hW2hdO0koZyE9PU4pSShnLlA+ZCkxTjtZIEkoZy5QPT1jLlAmJmcuTD5jLkwpYVtiXT1OO1kgSShnLlA+PWMuUCYmZy5QPGQpYVtoXT1OfUggYX0sNGQ6NihhKXtLIGI9W10sYz0ydShKLlYoIjJpLTFzIikpO3YoYSw2KGQsaCl7Yi5VKGgrYyl9KTtIIGJ9LDNVOjYoYSl7SyBiPUouVigiMU0iLFtdKTtJKDFqIGIhPSIybSImJmIuVT09TiliPVtiXTthOnthPWEuMXEoKTtLIGM9M1cgMDtPKGM9Yz0xUS42YyhjfHwwLDApO2M8Yi5MO2MrKylJKGJbY109PWEpe2I9YzsxTiBhfWI9LTF9SCBiIT0tMX0sMnI6NihhLGIsYyl7YT1bIjFzIiwiNmkiK2IsIlAiK2EsIjZyIisoYiUyPT0wPzE6MikuMXEoKV07Si4zVShiKSYmYS5VKCI2NyIpO2I9PTAmJmEuVSgiMU4iKTtIXCc8VCAxZz0iXCcrYS4xSygiICIpK1wnIj5cJytjKyI8L1Q+In0sM1E6NihhLGIpe0sgYz0iIixkPWEuMWUoIlxcbiIpLkwsaD0ydShKLlYoIjJpLTFzIikpLGc9Si5WKCIyei0xcy0ydCIpO0koZz09UilnPShoK2QtMSkuMXEoKS5MO1kgSSgzUihnKT09UilnPTA7TyhLIGk9MDtpPGQ7aSsrKXtLIGs9Yj9iW2ldOmgraSxqO0koaz09MClqPWUuMTMuMVc7WXtqPWc7TyhLIGw9ay4xcSgpO2wuTDxqOylsPSIwIitsO2o9bH1hPWo7Yys9Si4ycihpLGssYSl9SCBjfSw0OTo2KGEsYil7YT14KGEpO0sgYz1hLjFlKCJcXG4iKTtKLlYoIjJ6LTFzLTJ0Iik7SyBkPTJ1KEouVigiMmktMXMiKSk7YT0iIjtPKEsgaD1KLlYoIjFEIiksZz0wO2c8Yy5MO2crKyl7SyBpPWNbZ10saz0vXigmMnM7fFxccykrLy5YKGkpLGo9TixsPWI/YltnXTpkK2c7SShrIT1OKXtqPWtbMF0uMXEoKTtpPWkuMW8oai5MKTtqPWouUSgiICIsZS4xMy4xVyl9aT14KGkpO0koaS5MPT0wKWk9ZS4xMy4xVzthKz1KLjJyKGcsbCwoaiE9Tj9cJzwxNyAxZz0iXCcraCtcJyA1TiI+XCcraisiPC8xNz4iOiIiKStpKX1IIGF9LDRmOjYoYSl7SCBhPyI8NGE+IithKyI8LzRhPiI6IiJ9LDRiOjYoYSxiKXs2IGMobCl7SChsPWw/bC4xVnx8ZzpnKT9sKyIgIjoiIn1PKEsgZD0wLGg9IiIsZz1KLlYoIjFEIiwiIiksaT0wO2k8Yi5MO2krKyl7SyBrPWJbaV0sajtJKCEoaz09PU58fGsuTD09PTApKXtqPWMoayk7aCs9dShhLjFvKGQsay5QLWQpLGorIjQ4IikrdShrLjFULGoray4yMyk7ZD1rLlAray5MKyhrLjc1fHwwKX19aCs9dShhLjFvKGQpLGMoKSsiNDgiKTtIIGh9LDFIOjYoYSl7SyBiPSIiLGM9WyIyMCJdLGQ7SShKLlYoIjJrIik9PVIpSi4xbi4xNj1KLjFuLjF1PTExOzFsPSIyMCI7Si5WKCIybCIpPT1SJiZjLlUoIjQ3Iik7SSgoMXU9Si5WKCIxdSIpKT09MTEpYy5VKCI2UyIpO2MuVShKLlYoIjFnLTI3IikpO2MuVShKLlYoIjFEIikpO2E9YS5RKC9eWyBdKltcXG5dK3xbXFxuXSpbIF0qJC9nLCIiKS5RKC9cXHIvZywiICIpO2I9Si5WKCI0My0yMiIpO0koSi5WKCI0Mi00NSIpPT1SKWE9bihhLGIpO1l7TyhLIGg9IiIsZz0wO2c8YjtnKyspaCs9IiAiO2E9YS5RKC9cXHQvZyxoKX1hPWE7YTp7Yj1hPWE7aD0vPDJSXFxzKlxcLz8+fCYxeTsyUlxccypcXC8/JjFHOy8yVDtJKGUuMTMuNDY9PVIpYj1iLlEoaCwiXFxuIik7SShlLjEzLjQ0PT1SKWI9Yi5RKGgsIiIpO2I9Yi4xZSgiXFxuIik7aD0vXlxccyovO2c9NFE7TyhLIGk9MDtpPGIuTCYmZz4wO2krKyl7SyBrPWJbaV07SSh4KGspLkwhPTApe2s9aC5YKGspO0koaz09Til7YT1hOzFOIGF9Zz0xUS40cShrWzBdLkwsZyl9fUkoZz4wKU8oaT0wO2k8Yi5MO2krKyliW2ldPWJbaV0uMW8oZyk7YT1iLjFLKCJcXG4iKX1JKDF1KWQ9Si40ZChhKTtiPUouNGMoSi4ySixhKTtiPUouNGIoYSxiKTtiPUouNDkoYixkKTtJKEouVigiNDEtNDAiKSliPUUoYik7MWogMkghPSIxZCImJjJILjNTJiYySC4zUy4xQygvNXMvKSYmYy5VKCI1dCIpO0ggYj1cJzxUIDFjPSJcJyt0KEouMWMpK1wnIiAxZz0iXCcrYy4xSygiICIpK1wnIj5cJysoSi5WKCIxNiIpP2UuMTYuMUgoSik6IiIpK1wnPDNaIDV6PSIwIiA1SD0iMCIgNUo9IjAiPlwnK0ouNGYoSi5WKCIxdCIpKSsiPDNUPjwzUD4iKygxdT9cJzwyZCAxZz0iMXUiPlwnK0ouM1EoYSkrIjwvMmQ+IjoiIikrXCc8MmQgMWc9IjE3Ij48VCAxZz0iM08iPlwnK2IrIjwvVD48LzJkPjwvM1A+PC8zVD48LzNaPjwvVD4ifSwyRjo2KGEpe0koYT09PU4pYT0iIjtKLjE3PWE7SyBiPUouM1koIlQiKTtiLjNYPUouMUgoYSk7Si5WKCIxNiIpJiZ3KHAoYiwiLjE2IiksIjVjIixlLjE2LjJiKTtKLlYoIjNWLTE3IikmJncocChiLCIuMTciKSwiNTYiLGYpO0ggYn0sMlE6NihhKXtKLjFjPSIiKzFRLjVkKDFRLjVuKCkqNWspLjFxKCk7ZS4xWS4yQVt0KEouMWMpXT1KO0ouMW49QyhlLjJ2LGF8fHt9KTtJKEouVigiMmsiKT09UilKLjFuLjE2PUouMW4uMXU9MTF9LDVqOjYoYSl7YT1hLlEoL15cXHMrfFxccyskL2csIiIpLlEoL1xccysvZywifCIpO0giXFxcXGIoPzoiK2ErIilcXFxcYiJ9LDVmOjYoYSl7Si4yOD17MTg6ezFJOmEuMTgsMjM6IjFrIn0sMWI6ezFJOmEuMWIsMjM6IjFrIn0sMTc6MWYgTSgiKD88MTg+IithLjE4LjFtKyIpKD88MTc+Lio/KSg/PDFiPiIrYS4xYi4xbSsiKSIsIjVvIil9fX07SCBlfSgpOzFqIDJlIT0iMWQiJiYoMmUuMXY9MXYpOycsNjIsNDQxLCd8fHx8fHxmdW5jdGlvbnx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHxyZXR1cm58aWZ8dGhpc3x2YXJ8bGVuZ3RofFhSZWdFeHB8bnVsbHxmb3J8aW5kZXh8cmVwbGFjZXx0cnVlfHxkaXZ8cHVzaHxnZXRQYXJhbXxjYWxsfGV4ZWN8ZWxzZXxwcm90b3R5cGV8fGZhbHNlfGxhc3RJbmRleHxjb25maWd8YXJndW1lbnRzfFJlZ0V4cHx0b29sYmFyfGNvZGV8bGVmdHxjYXB0dXJlTmFtZXN8c2xpY2V8cmlnaHR8aWR8dW5kZWZpbmVkfHNwbGl0fG5ld3xjbGFzc3xhZGRUb2tlbnxpbmRleE9mfHR5cGVvZnxzY3JpcHR8Y2xhc3NOYW1lfHNvdXJjZXxwYXJhbXN8c3Vic3RyfGFwcGx5fHRvU3RyaW5nfFN0cmluZ3xsaW5lfHRpdGxlfGd1dHRlcnxTeW50YXhIaWdobGlnaHRlcnxfeHJlZ2V4cHxzdHJpbmdzfGx0fGh0bWx8dGVzdHxPVVRTSURFX0NMQVNTfG1hdGNofGJydXNofGRvY3VtZW50fHRhcmdldHxndHxnZXRIdG1sfHJlZ2V4fGdsb2JhbHxqb2lufHN0eWxlfGhpZ2hsaWdodHxicmVha3xjb25jYXR8d2luZG93fE1hdGh8aXNSZWdFeHB8dGhyb3d8dmFsdWV8YnJ1c2hlc3xicnVzaE5hbWV8c3BhY2V8YWxlcnR8dmFyc3xodHRwfHN5bnRheGhpZ2hsaWdodGVyfGV4cGFuZFNvdXJjZXxzaXplfGNzc3xjYXNlfGZvbnR8RmF8bmFtZXxodG1sU2NyaXB0fGRBfGNhbnxoYW5kbGVyfGdtfHRkfGV4cG9ydHN8Y29sb3J8aW58aHJlZnxmaXJzdHxkaXNjb3ZlcmVkQnJ1c2hlc3xsaWdodHxjb2xsYXBzZXxvYmplY3R8Y2FjaGV8Z2V0QnV0dG9uSHRtbHx0cmlnZ2VyfHBhdHRlcm58Z2V0TGluZUh0bWx8bmJzcHxudW1iZXJzfHBhcnNlSW50fGRlZmF1bHRzfGNvbXxpdGVtc3x3d3d8cGFkfGhpZ2hsaWdodGVyc3xleGVjdXRlfGZvY3VzfGZ1bmN8YWxsfGdldERpdnxwYXJlbnROb2RlfG5hdmlnYXRvcnxJTlNJREVfQ0xBU1N8cmVnZXhMaXN0fGhhc0ZsYWd8TWF0Y2h8dXNlU2NyaXB0VGFnc3xoYXNOYW1lZENhcHR1cmV8dGV4dHxoZWxwfGluaXR8YnJ8aW5wdXR8Z2l8RXJyb3J8dmFsdWVzfHNwYW58bGlzdHwyNTB8aGVpZ2h0fHdpZHRofHNjcmVlbnx0b3B8NTAwfHRhZ05hbWV8ZmluZEVsZW1lbnRzfGdldEVsZW1lbnRzQnlUYWdOYW1lfGFib3V0RGlhbG9nfF9ibGFua3xhcHBlbmRDaGlsZHxjaGFyQXR8QXJyYXl8Y29weUFzR2xvYmFsfHNldEZsYWd8aGlnaGxpZ2h0ZXJffHN0cmluZ3xhdHRhY2hFdmVudHxub2RlTmFtZXxmbG9vcnxiYWNrcmVmfG91dHB1dHx0aGV8VHlwZUVycm9yfHN0aWNreXxaYXxpdGVyYXRlfGZyZWV6ZVRva2Vuc3xzY29wZXx0eXBlfHRleHRhcmVhfGFsZXhnb3JiYXRjaGV2fHZlcnNpb258bWFyZ2lufDIwMTB8MDA1ODk2fGdzfHJlZ2V4TGlifGJvZHl8Y2VudGVyfGFsaWdufG5vQnJ1c2h8cmVxdWlyZXxjaGlsZE5vZGVzfERURHx4aHRtbDF8aGVhZHxvcmd8dzN8dXJsfHByZXZlbnREZWZhdWx0fGNvbnRhaW5lcnx0cnxnZXRMaW5lTnVtYmVyc0h0bWx8aXNOYU58dXNlckFnZW50fHRib2R5fGlzTGluZUhpZ2hsaWdodGVkfHF1aWNrfHZvaWR8aW5uZXJIVE1MfGNyZWF0ZXx0YWJsZXxsaW5rc3xhdXRvfHNtYXJ0fHRhYnxzdHJpcEJyc3x0YWJzfGJsb2dnZXJNb2RlfGNvbGxhcHNlZHxwbGFpbnxnZXRDb2RlTGluZXNIdG1sfGNhcHRpb258Z2V0TWF0Y2hlc0h0bWx8ZmluZE1hdGNoZXN8ZmlndXJlT3V0TGluZU51bWJlcnN8cmVtb3ZlTmVzdGVkTWF0Y2hlc3xnZXRUaXRsZUh0bWx8YnJ1c2hOb3RIdG1sU2NyaXB0fHN1YnN0cmluZ3xjcmVhdGVFbGVtZW50fEhpZ2hsaWdodGVyfGxvYWR8SHRtbFNjcmlwdHxCcnVzaHxwcmV8ZXhwYW5kfG11bHRpbGluZXxtaW58Q2FufGlnbm9yZUNhc2V8ZmluZHxibHVyfGV4dGVuZGVkfHRvTG93ZXJDYXNlfGFsaWFzZXN8YWRkRXZlbnRMaXN0ZW5lcnxpbm5lclRleHR8dGV4dENvbnRlbnR8d2FzbnxzZWxlY3R8Y3JlYXRlVGV4dE5vZGV8cmVtb3ZlQ2hpbGR8b3B0aW9ufHNhbWV8ZnJhbWV8eG1sbnN8ZHRkfHR3aWNlfDE5OTl8ZXF1aXZ8bWV0YXxodG1sc2NyaXB0fHRyYW5zaXRpb25hbHwxRTN8ZXhwZWN0ZWR8UFVCTElDfERPQ1RZUEV8b258VzNDfFhIVE1MfFRSfEVOfFRyYW5zaXRpb25hbHx8Y29uZmlndXJlZHxzcmNFbGVtZW50fE9iamVjdHxhZnRlcnxydW58ZGJsY2xpY2t8bWF0Y2hDaGFpbnx2YWx1ZU9mfGNvbnN0cnVjdG9yfGRlZmF1bHR8c3dpdGNofGNsaWNrfHJvdW5kfGV4ZWNBdHxmb3JIdG1sU2NyaXB0fHRva2VufGdpbXl8ZnVuY3Rpb25zfGdldEtleXdvcmRzfDFFNnxlc2NhcGV8d2l0aGlufHJhbmRvbXxzZ2l8YW5vdGhlcnxmaW5hbGx5fHN1cHBseXxNU0lFfGllfHRvVXBwZXJDYXNlfGNhdGNofHJldHVyblZhbHVlfGRlZmluaXRpb258ZXZlbnR8Ym9yZGVyfGltc3h8Y29uc3RydWN0aW5nfG9uZXxJbmZpbml0eXxmcm9tfHdoZW58Q29udGVudHxjZWxscGFkZGluZ3xmbGFnc3xjZWxsc3BhY2luZ3x0cnl8eGh0bWx8VHlwZXxzcGFjZXN8MjkzMDQwMnxob3N0ZWRfYnV0dG9uX2lkfGxhc3RJbmRleE9mfGRvbmF0ZXxhY3RpdmV8ZGV2ZWxvcG1lbnR8a2VlcHx0b3x4Y2xpY2t8X3N8WG1sfHBsZWFzZXxsaWtlfHlvdXxwYXlwYWx8Y2dpfGNtZHx3ZWJzY3J8YmlufGhpZ2hsaWdodGVkfHNjcm9sbGJhcnN8YXNwU2NyaXB0VGFnc3xwaHBTY3JpcHRUYWdzfHNvcnR8bWF4fHNjcmlwdFNjcmlwdFRhZ3N8dG9vbGJhcl9pdGVtfF98Y29tbWFuZHxjb21tYW5kX3xudW1iZXJ8Z2V0RWxlbWVudEJ5SWR8ZG91YmxlUXVvdGVkU3RyaW5nfHNpbmdsZUxpbmVQZXJsQ29tbWVudHN8c2luZ2xlTGluZUNDb21tZW50c3xtdWx0aUxpbmVDQ29tbWVudHN8c2luZ2xlUXVvdGVkU3RyaW5nfG11bHRpTGluZURvdWJsZVF1b3RlZFN0cmluZ3x4bWxDb21tZW50c3xhbHR8bXVsdGlMaW5lU2luZ2xlUXVvdGVkU3RyaW5nfElmfGh0dHBzfDFlbXwwMDB8ZmZmfGJhY2tncm91bmR8NWVtfHh4fGJvdHRvbXw3NWVtfEdvcmJhdGNoZXZ8bGFyZ2V8c2VyaWZ8Q0RBVEF8Y29udGludWV8dXRmfGNoYXJzZXR8Y29udGVudHxBYm91dHxmYW1pbHl8c2Fuc3xIZWx2ZXRpY2F8QXJpYWx8R2VuZXZhfDNlbXxub2d1dHRlcnxDb3B5cmlnaHR8c3ludGF4fGNsb3NlfHdyaXRlfDIwMDR8QWxleHxvcGVufEphdmFTY3JpcHR8aGlnaGxpZ2h0ZXJ8SnVseXwwMnxyZXBsYWNlQ2hpbGR8b2Zmc2V0fDgzJy5zcGxpdCgnfCcpLDAse30pKQo%3D"

shbrushpython = "data:application/x-javascript;base64,LyoqCiAqIFN5bnRheEhpZ2hsaWdodGVyCiAqIGh0dHA6Ly9hbGV4Z29yYmF0Y2hldi5jb20vU3ludGF4SGlnaGxpZ2h0ZXIKICoKICogU3ludGF4SGlnaGxpZ2h0ZXIgaXMgZG9uYXRpb253YXJlLiBJZiB5b3UgYXJlIHVzaW5nIGl0LCBwbGVhc2UgZG9uYXRlLgogKiBodHRwOi8vYWxleGdvcmJhdGNoZXYuY29tL1N5bnRheEhpZ2hsaWdodGVyL2RvbmF0ZS5odG1sCiAqCiAqIEB2ZXJzaW9uCiAqIDMuMC44MyAoSnVseSAwMiAyMDEwKQogKiAKICogQGNvcHlyaWdodAogKiBDb3B5cmlnaHQgKEMpIDIwMDQtMjAxMCBBbGV4IEdvcmJhdGNoZXYuCiAqCiAqIEBsaWNlbnNlCiAqIER1YWwgbGljZW5zZWQgdW5kZXIgdGhlIE1JVCBhbmQgR1BMIGxpY2Vuc2VzLgogKi8KOyhmdW5jdGlvbigpCnsKCS8vIENvbW1vbkpTCgl0eXBlb2YocmVxdWlyZSkgIT0gJ3VuZGVmaW5lZCcgPyBTeW50YXhIaWdobGlnaHRlciA9IHJlcXVpcmUoJ3NoQ29yZScpLlN5bnRheEhpZ2hsaWdodGVyIDogbnVsbDsKCglmdW5jdGlvbiBCcnVzaCgpCgl7CgkJLy8gQ29udHJpYnV0ZWQgYnkgR2hlb3JnaGUgTWlsYXMgYW5kIEFobWFkIFNoZXJpZgoJCgkJdmFyIGtleXdvcmRzID0gICdhbmQgYXNzZXJ0IGJyZWFrIGNsYXNzIGNvbnRpbnVlIGRlZiBkZWwgZWxpZiBlbHNlICcgKwoJCQkJCQknZXhjZXB0IGV4ZWMgZmluYWxseSBmb3IgZnJvbSBnbG9iYWwgaWYgaW1wb3J0IGluIGlzICcgKwoJCQkJCQknbGFtYmRhIG5vdCBvciBwYXNzIHByaW50IHJhaXNlIHJldHVybiB0cnkgeWllbGQgd2hpbGUnOwoKCQl2YXIgZnVuY3MgPSAnX19pbXBvcnRfXyBhYnMgYWxsIGFueSBhcHBseSBiYXNlc3RyaW5nIGJpbiBib29sIGJ1ZmZlciBjYWxsYWJsZSAnICsKCQkJCQknY2hyIGNsYXNzbWV0aG9kIGNtcCBjb2VyY2UgY29tcGlsZSBjb21wbGV4IGRlbGF0dHIgZGljdCBkaXIgJyArCgkJCQkJJ2Rpdm1vZCBlbnVtZXJhdGUgZXZhbCBleGVjZmlsZSBmaWxlIGZpbHRlciBmbG9hdCBmb3JtYXQgZnJvemVuc2V0ICcgKwoJCQkJCSdnZXRhdHRyIGdsb2JhbHMgaGFzYXR0ciBoYXNoIGhlbHAgaGV4IGlkIGlucHV0IGludCBpbnRlcm4gJyArCgkJCQkJJ2lzaW5zdGFuY2UgaXNzdWJjbGFzcyBpdGVyIGxlbiBsaXN0IGxvY2FscyBsb25nIG1hcCBtYXggbWluIG5leHQgJyArCgkJCQkJJ29iamVjdCBvY3Qgb3BlbiBvcmQgcG93IHByaW50IHByb3BlcnR5IHJhbmdlIHJhd19pbnB1dCByZWR1Y2UgJyArCgkJCQkJJ3JlbG9hZCByZXByIHJldmVyc2VkIHJvdW5kIHNldCBzZXRhdHRyIHNsaWNlIHNvcnRlZCBzdGF0aWNtZXRob2QgJyArCgkJCQkJJ3N0ciBzdW0gc3VwZXIgdHVwbGUgdHlwZSB0eXBlIHVuaWNociB1bmljb2RlIHZhcnMgeHJhbmdlIHppcCc7CgoJCXZhciBzcGVjaWFsID0gICdOb25lIFRydWUgRmFsc2Ugc2VsZiBjbHMgY2xhc3NfJzsKCgkJdGhpcy5yZWdleExpc3QgPSBbCgkJCQl7IHJlZ2V4OiBTeW50YXhIaWdobGlnaHRlci5yZWdleExpYi5zaW5nbGVMaW5lUGVybENvbW1lbnRzLCBjc3M6ICdjb21tZW50cycgfSwKCQkJCXsgcmVnZXg6IC9eXHMqQFx3Ky9nbSwgCQkJCQkJCQkJCWNzczogJ2RlY29yYXRvcicgfSwKCQkJCXsgcmVnZXg6IC8oWydcIl17M30pKFteXDFdKSo/XDEvZ20sIAkJCQkJCWNzczogJ2NvbW1lbnRzJyB9LAoJCQkJeyByZWdleDogLyIoPyEiKSg/OlwufFxcXCJ8W15cIiJcbl0pKiIvZ20sIAkJCQkJY3NzOiAnc3RyaW5nJyB9LAoJCQkJeyByZWdleDogLycoPyEnKSg/OlwufChcXFwnKXxbXlwnJ1xuXSkqJy9nbSwgCQkJCWNzczogJ3N0cmluZycgfSwKCQkJCXsgcmVnZXg6IC9cK3xcLXxcKnxcL3xcJXw9fD09L2dtLCAJCQkJCQkJY3NzOiAna2V5d29yZCcgfSwKCQkJCXsgcmVnZXg6IC9cYlxkK1wuP1x3Ki9nLCAJCQkJCQkJCQljc3M6ICd2YWx1ZScgfSwKCQkJCXsgcmVnZXg6IG5ldyBSZWdFeHAodGhpcy5nZXRLZXl3b3JkcyhmdW5jcyksICdnbWknKSwJCWNzczogJ2Z1bmN0aW9ucycgfSwKCQkJCXsgcmVnZXg6IG5ldyBSZWdFeHAodGhpcy5nZXRLZXl3b3JkcyhrZXl3b3JkcyksICdnbScpLCAJCWNzczogJ2tleXdvcmQnIH0sCgkJCQl7IHJlZ2V4OiBuZXcgUmVnRXhwKHRoaXMuZ2V0S2V5d29yZHMoc3BlY2lhbCksICdnbScpLCAJCWNzczogJ2NvbG9yMScgfQoJCQkJXTsKCQkJCgkJdGhpcy5mb3JIdG1sU2NyaXB0KFN5bnRheEhpZ2hsaWdodGVyLnJlZ2V4TGliLmFzcFNjcmlwdFRhZ3MpOwoJfTsKCglCcnVzaC5wcm90b3R5cGUJPSBuZXcgU3ludGF4SGlnaGxpZ2h0ZXIuSGlnaGxpZ2h0ZXIoKTsKCUJydXNoLmFsaWFzZXMJPSBbJ3B5JywgJ3B5dGhvbiddOwoKCVN5bnRheEhpZ2hsaWdodGVyLmJydXNoZXMuUHl0aG9uID0gQnJ1c2g7CgoJLy8gQ29tbW9uSlMKCXR5cGVvZihleHBvcnRzKSAhPSAndW5kZWZpbmVkJyA/IGV4cG9ydHMuQnJ1c2ggPSBCcnVzaCA6IG51bGw7Cn0pKCk7Cg%3D%3D"

shcorecss = "data:text/css;base64,LyoqCiAqIFN5bnRheEhpZ2hsaWdodGVyCiAqIGh0dHA6Ly9hbGV4Z29yYmF0Y2hldi5jb20vU3ludGF4SGlnaGxpZ2h0ZXIKICoKICogU3ludGF4SGlnaGxpZ2h0ZXIgaXMgZG9uYXRpb253YXJlLiBJZiB5b3UgYXJlIHVzaW5nIGl0LCBwbGVhc2UgZG9uYXRlLgogKiBodHRwOi8vYWxleGdvcmJhdGNoZXYuY29tL1N5bnRheEhpZ2hsaWdodGVyL2RvbmF0ZS5odG1sCiAqCiAqIEB2ZXJzaW9uCiAqIDMuMC44MyAoSnVseSAwMiAyMDEwKQogKiAKICogQGNvcHlyaWdodAogKiBDb3B5cmlnaHQgKEMpIDIwMDQtMjAxMCBBbGV4IEdvcmJhdGNoZXYuCiAqCiAqIEBsaWNlbnNlCiAqIER1YWwgbGljZW5zZWQgdW5kZXIgdGhlIE1JVCBhbmQgR1BMIGxpY2Vuc2VzLgogKi8KLnN5bnRheGhpZ2hsaWdodGVyIGEsCi5zeW50YXhoaWdobGlnaHRlciBkaXYsCi5zeW50YXhoaWdobGlnaHRlciBjb2RlLAouc3ludGF4aGlnaGxpZ2h0ZXIgdGFibGUsCi5zeW50YXhoaWdobGlnaHRlciB0YWJsZSB0ZCwKLnN5bnRheGhpZ2hsaWdodGVyIHRhYmxlIHRyLAouc3ludGF4aGlnaGxpZ2h0ZXIgdGFibGUgdGJvZHksCi5zeW50YXhoaWdobGlnaHRlciB0YWJsZSB0aGVhZCwKLnN5bnRheGhpZ2hsaWdodGVyIHRhYmxlIGNhcHRpb24sCi5zeW50YXhoaWdobGlnaHRlciB0ZXh0YXJlYSB7CiAgLW1vei1ib3JkZXItcmFkaXVzOiAwIDAgMCAwICFpbXBvcnRhbnQ7CiAgLXdlYmtpdC1ib3JkZXItcmFkaXVzOiAwIDAgMCAwICFpbXBvcnRhbnQ7CiAgYmFja2dyb3VuZDogbm9uZSAhaW1wb3J0YW50OwogIGJvcmRlcjogMCAhaW1wb3J0YW50OwogIGJvdHRvbTogYXV0byAhaW1wb3J0YW50OwogIGZsb2F0OiBub25lICFpbXBvcnRhbnQ7CiAgaGVpZ2h0OiBhdXRvICFpbXBvcnRhbnQ7CiAgbGVmdDogYXV0byAhaW1wb3J0YW50OwogIGxpbmUtaGVpZ2h0OiAxLjFlbSAhaW1wb3J0YW50OwogIG1hcmdpbjogMCAhaW1wb3J0YW50OwogIG91dGxpbmU6IDAgIWltcG9ydGFudDsKICBvdmVyZmxvdzogdmlzaWJsZSAhaW1wb3J0YW50OwogIHBhZGRpbmc6IDAgIWltcG9ydGFudDsKICBwb3NpdGlvbjogc3RhdGljICFpbXBvcnRhbnQ7CiAgcmlnaHQ6IGF1dG8gIWltcG9ydGFudDsKICB0ZXh0LWFsaWduOiBsZWZ0ICFpbXBvcnRhbnQ7CiAgdG9wOiBhdXRvICFpbXBvcnRhbnQ7CiAgdmVydGljYWwtYWxpZ246IGJhc2VsaW5lICFpbXBvcnRhbnQ7CiAgd2lkdGg6IGF1dG8gIWltcG9ydGFudDsKICBib3gtc2l6aW5nOiBjb250ZW50LWJveCAhaW1wb3J0YW50OwogIGZvbnQtZmFtaWx5OiAiQ29uc29sYXMiLCAiQml0c3RyZWFtIFZlcmEgU2FucyBNb25vIiwgIkNvdXJpZXIgTmV3IiwgQ291cmllciwgbW9ub3NwYWNlICFpbXBvcnRhbnQ7CiAgZm9udC13ZWlnaHQ6IG5vcm1hbCAhaW1wb3J0YW50OwogIGZvbnQtc3R5bGU6IG5vcm1hbCAhaW1wb3J0YW50OwogIGZvbnQtc2l6ZTogMWVtICFpbXBvcnRhbnQ7CiAgbWluLWhlaWdodDogaW5oZXJpdCAhaW1wb3J0YW50OwogIG1pbi1oZWlnaHQ6IGF1dG8gIWltcG9ydGFudDsKfQoKLnN5bnRheGhpZ2hsaWdodGVyIHsKICB3aWR0aDogMTAwJSAhaW1wb3J0YW50OwogIG1hcmdpbjogMWVtIDAgMWVtIDAgIWltcG9ydGFudDsKICBwb3NpdGlvbjogcmVsYXRpdmUgIWltcG9ydGFudDsKICBvdmVyZmxvdzogYXV0byAhaW1wb3J0YW50OwogIGZvbnQtc2l6ZTogMWVtICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLnNvdXJjZSB7CiAgb3ZlcmZsb3c6IGhpZGRlbiAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAuYm9sZCB7CiAgZm9udC13ZWlnaHQ6IGJvbGQgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLml0YWxpYyB7CiAgZm9udC1zdHlsZTogaXRhbGljICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyIC5saW5lIHsKICB3aGl0ZS1zcGFjZTogcHJlICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyIHRhYmxlIHsKICB3aWR0aDogMTAwJSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciB0YWJsZSBjYXB0aW9uIHsKICB0ZXh0LWFsaWduOiBsZWZ0ICFpbXBvcnRhbnQ7CiAgcGFkZGluZzogLjVlbSAwIDAuNWVtIDFlbSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciB0YWJsZSB0ZC5jb2RlIHsKICB3aWR0aDogMTAwJSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciB0YWJsZSB0ZC5jb2RlIC5jb250YWluZXIgewogIHBvc2l0aW9uOiByZWxhdGl2ZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciB0YWJsZSB0ZC5jb2RlIC5jb250YWluZXIgdGV4dGFyZWEgewogIGJveC1zaXppbmc6IGJvcmRlci1ib3ggIWltcG9ydGFudDsKICBwb3NpdGlvbjogYWJzb2x1dGUgIWltcG9ydGFudDsKICBsZWZ0OiAwICFpbXBvcnRhbnQ7CiAgdG9wOiAwICFpbXBvcnRhbnQ7CiAgd2lkdGg6IDEwMCUgIWltcG9ydGFudDsKICBoZWlnaHQ6IDEwMCUgIWltcG9ydGFudDsKICBib3JkZXI6IG5vbmUgIWltcG9ydGFudDsKICBiYWNrZ3JvdW5kOiB3aGl0ZSAhaW1wb3J0YW50OwogIHBhZGRpbmctbGVmdDogMWVtICFpbXBvcnRhbnQ7CiAgb3ZlcmZsb3c6IGhpZGRlbiAhaW1wb3J0YW50OwogIHdoaXRlLXNwYWNlOiBwcmUgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgdGFibGUgdGQuZ3V0dGVyIC5saW5lIHsKICB0ZXh0LWFsaWduOiByaWdodCAhaW1wb3J0YW50OwogIHBhZGRpbmc6IDAgMC41ZW0gMCAxZW0gIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgdGFibGUgdGQuY29kZSAubGluZSB7CiAgcGFkZGluZzogMCAxZW0gIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIubm9ndXR0ZXIgdGQuY29kZSAuY29udGFpbmVyIHRleHRhcmVhLCAuc3ludGF4aGlnaGxpZ2h0ZXIubm9ndXR0ZXIgdGQuY29kZSAubGluZSB7CiAgcGFkZGluZy1sZWZ0OiAwZW0gIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIuc2hvdyB7CiAgZGlzcGxheTogYmxvY2sgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIuY29sbGFwc2VkIHRhYmxlIHsKICBkaXNwbGF5OiBub25lICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLmNvbGxhcHNlZCAudG9vbGJhciB7CiAgcGFkZGluZzogMC4xZW0gMC44ZW0gMGVtIDAuOGVtICFpbXBvcnRhbnQ7CiAgZm9udC1zaXplOiAxZW0gIWltcG9ydGFudDsKICBwb3NpdGlvbjogc3RhdGljICFpbXBvcnRhbnQ7CiAgd2lkdGg6IGF1dG8gIWltcG9ydGFudDsKICBoZWlnaHQ6IGF1dG8gIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIuY29sbGFwc2VkIC50b29sYmFyIHNwYW4gewogIGRpc3BsYXk6IGlubGluZSAhaW1wb3J0YW50OwogIG1hcmdpbi1yaWdodDogMWVtICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLmNvbGxhcHNlZCAudG9vbGJhciBzcGFuIGEgewogIHBhZGRpbmc6IDAgIWltcG9ydGFudDsKICBkaXNwbGF5OiBub25lICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLmNvbGxhcHNlZCAudG9vbGJhciBzcGFuIGEuZXhwYW5kU291cmNlIHsKICBkaXNwbGF5OiBpbmxpbmUgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLnRvb2xiYXIgewogIHBvc2l0aW9uOiBhYnNvbHV0ZSAhaW1wb3J0YW50OwogIHJpZ2h0OiAxcHggIWltcG9ydGFudDsKICB0b3A6IDFweCAhaW1wb3J0YW50OwogIHdpZHRoOiAxMXB4ICFpbXBvcnRhbnQ7CiAgaGVpZ2h0OiAxMXB4ICFpbXBvcnRhbnQ7CiAgZm9udC1zaXplOiAxMHB4ICFpbXBvcnRhbnQ7CiAgei1pbmRleDogMTAgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLnRvb2xiYXIgc3Bhbi50aXRsZSB7CiAgZGlzcGxheTogaW5saW5lICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyIC50b29sYmFyIGEgewogIGRpc3BsYXk6IGJsb2NrICFpbXBvcnRhbnQ7CiAgdGV4dC1hbGlnbjogY2VudGVyICFpbXBvcnRhbnQ7CiAgdGV4dC1kZWNvcmF0aW9uOiBub25lICFpbXBvcnRhbnQ7CiAgcGFkZGluZy10b3A6IDFweCAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAudG9vbGJhciBhLmV4cGFuZFNvdXJjZSB7CiAgZGlzcGxheTogbm9uZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5pZSB7CiAgZm9udC1zaXplOiAuOWVtICFpbXBvcnRhbnQ7CiAgcGFkZGluZzogMXB4IDAgMXB4IDAgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIuaWUgLnRvb2xiYXIgewogIGxpbmUtaGVpZ2h0OiA4cHggIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIuaWUgLnRvb2xiYXIgYSB7CiAgcGFkZGluZy10b3A6IDBweCAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAubGluZS5hbHQxIC5jb250ZW50LAouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLmxpbmUuYWx0MiAuY29udGVudCwKLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIC5saW5lLmhpZ2hsaWdodGVkIC5udW1iZXIsCi5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAubGluZS5oaWdobGlnaHRlZC5hbHQxIC5jb250ZW50LAouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLmxpbmUuaGlnaGxpZ2h0ZWQuYWx0MiAuY29udGVudCB7CiAgYmFja2dyb3VuZDogbm9uZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAubGluZSAubnVtYmVyIHsKICBjb2xvcjogI2JiYmJiYiAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAubGluZSAuY29udGVudCB7CiAgY29sb3I6IGJsYWNrICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIC50b29sYmFyIHsKICBkaXNwbGF5OiBub25lICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIGEgewogIHRleHQtZGVjb3JhdGlvbjogbm9uZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAucGxhaW4sIC5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAucGxhaW4gYSB7CiAgY29sb3I6IGJsYWNrICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIC5jb21tZW50cywgLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIC5jb21tZW50cyBhIHsKICBjb2xvcjogIzAwODIwMCAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAuc3RyaW5nLCAuc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLnN0cmluZyBhIHsKICBjb2xvcjogYmx1ZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAua2V5d29yZCB7CiAgY29sb3I6ICMwMDY2OTkgIWltcG9ydGFudDsKICBmb250LXdlaWdodDogYm9sZCAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAucHJlcHJvY2Vzc29yIHsKICBjb2xvcjogZ3JheSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAudmFyaWFibGUgewogIGNvbG9yOiAjYWE3NzAwICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIC52YWx1ZSB7CiAgY29sb3I6ICMwMDk5MDAgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLmZ1bmN0aW9ucyB7CiAgY29sb3I6ICNmZjE0OTMgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLmNvbnN0YW50cyB7CiAgY29sb3I6ICMwMDY2Y2MgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLnNjcmlwdCB7CiAgZm9udC13ZWlnaHQ6IGJvbGQgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLmNvbG9yMSwgLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIC5jb2xvcjEgYSB7CiAgY29sb3I6IGdyYXkgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLmNvbG9yMiwgLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIC5jb2xvcjIgYSB7CiAgY29sb3I6ICNmZjE0OTMgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIucHJpbnRpbmcgLmNvbG9yMywgLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIC5jb2xvcjMgYSB7CiAgY29sb3I6IHJlZCAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAuYnJlYWssIC5zeW50YXhoaWdobGlnaHRlci5wcmludGluZyAuYnJlYWsgYSB7CiAgY29sb3I6IGJsYWNrICFpbXBvcnRhbnQ7Cn0K"

shthemedefault = "data:text/css;base64,LyoqCiAqIFN5bnRheEhpZ2hsaWdodGVyCiAqIGh0dHA6Ly9hbGV4Z29yYmF0Y2hldi5jb20vU3ludGF4SGlnaGxpZ2h0ZXIKICoKICogU3ludGF4SGlnaGxpZ2h0ZXIgaXMgZG9uYXRpb253YXJlLiBJZiB5b3UgYXJlIHVzaW5nIGl0LCBwbGVhc2UgZG9uYXRlLgogKiBodHRwOi8vYWxleGdvcmJhdGNoZXYuY29tL1N5bnRheEhpZ2hsaWdodGVyL2RvbmF0ZS5odG1sCiAqCiAqIEB2ZXJzaW9uCiAqIDMuMC44MyAoSnVseSAwMiAyMDEwKQogKiAKICogQGNvcHlyaWdodAogKiBDb3B5cmlnaHQgKEMpIDIwMDQtMjAxMCBBbGV4IEdvcmJhdGNoZXYuCiAqCiAqIEBsaWNlbnNlCiAqIER1YWwgbGljZW5zZWQgdW5kZXIgdGhlIE1JVCBhbmQgR1BMIGxpY2Vuc2VzLgogKi8KLnN5bnRheGhpZ2hsaWdodGVyIHsKICBiYWNrZ3JvdW5kLWNvbG9yOiB3aGl0ZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAubGluZS5hbHQxIHsKICBiYWNrZ3JvdW5kLWNvbG9yOiB3aGl0ZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAubGluZS5hbHQyIHsKICBiYWNrZ3JvdW5kLWNvbG9yOiB3aGl0ZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAubGluZS5oaWdobGlnaHRlZC5hbHQxLCAuc3ludGF4aGlnaGxpZ2h0ZXIgLmxpbmUuaGlnaGxpZ2h0ZWQuYWx0MiB7CiAgYmFja2dyb3VuZC1jb2xvcjogI2UwZTBlMCAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAubGluZS5oaWdobGlnaHRlZC5udW1iZXIgewogIGNvbG9yOiBibGFjayAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciB0YWJsZSBjYXB0aW9uIHsKICBjb2xvcjogYmxhY2sgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLmd1dHRlciB7CiAgY29sb3I6ICNhZmFmYWYgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLmd1dHRlciAubGluZSB7CiAgYm9yZGVyLXJpZ2h0OiAzcHggc29saWQgIzZjZTI2YyAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAuZ3V0dGVyIC5saW5lLmhpZ2hsaWdodGVkIHsKICBiYWNrZ3JvdW5kLWNvbG9yOiAjNmNlMjZjICFpbXBvcnRhbnQ7CiAgY29sb3I6IHdoaXRlICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLnByaW50aW5nIC5saW5lIC5jb250ZW50IHsKICBib3JkZXI6IG5vbmUgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIuY29sbGFwc2VkIHsKICBvdmVyZmxvdzogdmlzaWJsZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5jb2xsYXBzZWQgLnRvb2xiYXIgewogIGNvbG9yOiBibHVlICFpbXBvcnRhbnQ7CiAgYmFja2dyb3VuZDogd2hpdGUgIWltcG9ydGFudDsKICBib3JkZXI6IDFweCBzb2xpZCAjNmNlMjZjICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyLmNvbGxhcHNlZCAudG9vbGJhciBhIHsKICBjb2xvcjogYmx1ZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlci5jb2xsYXBzZWQgLnRvb2xiYXIgYTpob3ZlciB7CiAgY29sb3I6IHJlZCAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAudG9vbGJhciB7CiAgY29sb3I6IHdoaXRlICFpbXBvcnRhbnQ7CiAgYmFja2dyb3VuZDogIzZjZTI2YyAhaW1wb3J0YW50OwogIGJvcmRlcjogbm9uZSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAudG9vbGJhciBhIHsKICBjb2xvcjogd2hpdGUgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLnRvb2xiYXIgYTpob3ZlciB7CiAgY29sb3I6IGJsYWNrICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyIC5wbGFpbiwgLnN5bnRheGhpZ2hsaWdodGVyIC5wbGFpbiBhIHsKICBjb2xvcjogYmxhY2sgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLmNvbW1lbnRzLCAuc3ludGF4aGlnaGxpZ2h0ZXIgLmNvbW1lbnRzIGEgewogIGNvbG9yOiAjMDA4MjAwICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyIC5zdHJpbmcsIC5zeW50YXhoaWdobGlnaHRlciAuc3RyaW5nIGEgewogIGNvbG9yOiBibHVlICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyIC5rZXl3b3JkIHsKICBjb2xvcjogIzAwNjY5OSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAucHJlcHJvY2Vzc29yIHsKICBjb2xvcjogZ3JheSAhaW1wb3J0YW50Owp9Ci5zeW50YXhoaWdobGlnaHRlciAudmFyaWFibGUgewogIGNvbG9yOiAjYWE3NzAwICFpbXBvcnRhbnQ7Cn0KLnN5bnRheGhpZ2hsaWdodGVyIC52YWx1ZSB7CiAgY29sb3I6ICMwMDk5MDAgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLmZ1bmN0aW9ucyB7CiAgY29sb3I6ICNmZjE0OTMgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLmNvbnN0YW50cyB7CiAgY29sb3I6ICMwMDY2Y2MgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLnNjcmlwdCB7CiAgZm9udC13ZWlnaHQ6IGJvbGQgIWltcG9ydGFudDsKICBjb2xvcjogIzAwNjY5OSAhaW1wb3J0YW50OwogIGJhY2tncm91bmQtY29sb3I6IG5vbmUgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLmNvbG9yMSwgLnN5bnRheGhpZ2hsaWdodGVyIC5jb2xvcjEgYSB7CiAgY29sb3I6IGdyYXkgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLmNvbG9yMiwgLnN5bnRheGhpZ2hsaWdodGVyIC5jb2xvcjIgYSB7CiAgY29sb3I6ICNmZjE0OTMgIWltcG9ydGFudDsKfQouc3ludGF4aGlnaGxpZ2h0ZXIgLmNvbG9yMywgLnN5bnRheGhpZ2hsaWdodGVyIC5jb2xvcjMgYSB7CiAgY29sb3I6IHJlZCAhaW1wb3J0YW50Owp9Cgouc3ludGF4aGlnaGxpZ2h0ZXIgLmtleXdvcmQgewogIGZvbnQtd2VpZ2h0OiBib2xkICFpbXBvcnRhbnQ7Cn0K"
