from .compat import escape
from .jsonify import encode

_builtin_renderers = {}
error_formatters = []

#
# JSON rendering engine
#


class JsonRenderer(object):
    '''
    Defines the builtin ``JSON`` renderer.
    '''
    def __init__(self, path, extra_vars):
        pass

    def render(self, template_path, namespace):
        '''
        Implements ``JSON`` rendering.
        '''
        return encode(namespace)

    # TODO: add error formatter for json (pass it through json lint?)

_builtin_renderers['json'] = JsonRenderer

#
# Genshi rendering engine
#

try:
    from genshi.template import (TemplateLoader,
                                 TemplateError as gTemplateError)

    class GenshiRenderer(object):
        '''
        Defines the builtin ``Genshi`` renderer.
        '''
        def __init__(self, path, extra_vars):
            self.loader = TemplateLoader([path], auto_reload=True)
            self.extra_vars = extra_vars

        def render(self, template_path, namespace):
            '''
            Implements ``Genshi`` rendering.
            '''
            tmpl = self.loader.load(template_path)
            stream = tmpl.generate(**self.extra_vars.make_ns(namespace))
            return stream.render('html')

    _builtin_renderers['genshi'] = GenshiRenderer

    def format_genshi_error(exc_value):
        '''
        Implements ``Genshi`` renderer error formatting.
        '''
        if isinstance(exc_value, (gTemplateError)):
            retval = '<h4>Genshi error %s</h4>' % escape(
                exc_value.args[0],
                True
            )
            retval += format_line_context(exc_value.filename, exc_value.lineno)
            return retval
    error_formatters.append(format_genshi_error)
except ImportError:                                 # pragma no cover
    pass


#
# Mako rendering engine
#

try:
    from mako.lookup import TemplateLookup
    from mako.exceptions import (CompileException, SyntaxException,
                                 html_error_template)

    class MakoRenderer(object):
        '''
        Defines the builtin ``Mako`` renderer.
        '''
        def __init__(self, path, extra_vars):
            self.loader = TemplateLookup(
                directories=[path],
                output_encoding='utf-8'
            )
            self.extra_vars = extra_vars

        def render(self, template_path, namespace):
            '''
            Implements ``Mako`` rendering.
            '''
            tmpl = self.loader.get_template(template_path)
            return tmpl.render(**self.extra_vars.make_ns(namespace))

    _builtin_renderers['mako'] = MakoRenderer

    def format_mako_error(exc_value):
        '''
        Implements ``Mako`` renderer error formatting.
        '''
        if isinstance(exc_value, (CompileException, SyntaxException)):
            return html_error_template().render(full=False, css=False)

    error_formatters.append(format_mako_error)
except ImportError:                                 # pragma no cover
    pass


#
# Kajiki rendering engine
#

try:
    from kajiki.loader import FileLoader

    class KajikiRenderer(object):
        '''
        Defines the builtin ``Kajiki`` renderer.
        '''
        def __init__(self, path, extra_vars):
            self.loader = FileLoader(path, reload=True)
            self.extra_vars = extra_vars

        def render(self, template_path, namespace):
            '''
            Implements ``Kajiki`` rendering.
            '''
            Template = self.loader.import_(template_path)
            stream = Template(self.extra_vars.make_ns(namespace))
            return stream.render()
    _builtin_renderers['kajiki'] = KajikiRenderer
    # TODO: add error formatter for kajiki
except ImportError:                                 # pragma no cover
    pass

#
# Jinja2 rendering engine
#
try:
    from jinja2 import Environment, FileSystemLoader
    from jinja2.exceptions import TemplateSyntaxError as jTemplateSyntaxError

    class JinjaRenderer(object):
        '''
        Defines the builtin ``Jinja`` renderer.
        '''
        def __init__(self, path, extra_vars):
            self.env = Environment(loader=FileSystemLoader(path))
            self.extra_vars = extra_vars

        def render(self, template_path, namespace):
            '''
            Implements ``Jinja`` rendering.
            '''
            template = self.env.get_template(template_path)
            return template.render(self.extra_vars.make_ns(namespace))
    _builtin_renderers['jinja'] = JinjaRenderer

    def format_jinja_error(exc_value):
        '''
        Implements ``Jinja`` renderer error formatting.
        '''
        retval = '<h4>Jinja2 error in \'%s\' on line %d</h4><div>%s</div>'
        if isinstance(exc_value, (jTemplateSyntaxError)):
            retval = retval % (
                exc_value.name,
                exc_value.lineno,
                exc_value.message
            )
            retval += format_line_context(exc_value.filename, exc_value.lineno)
            return retval
    error_formatters.append(format_jinja_error)
except ImportError:                                 # pragma no cover
    pass


#
# format helper function
#
def format_line_context(filename, lineno, context=10):
    '''
    Formats the the line context for error rendering.

    :param filename: the location of the file, within which the error occurred
    :param lineno: the offending line number
    :param context: number of lines of code to display before and after the
                    offending line.
    '''
    lines = open(filename).readlines()

    lineno = lineno - 1  # files are indexed by 1 not 0
    if lineno > 0:
        start_lineno = max(lineno - context, 0)
        end_lineno = lineno + context

        lines = [escape(l, True) for l in lines[start_lineno:end_lineno]]
        i = lineno - start_lineno
        lines[i] = '<strong>%s</strong>' % lines[i]

    else:
        lines = [escape(l, True) for l in lines[:context]]
    msg = '<pre style="background-color:#ccc;padding:2em;">%s</pre>'
    return msg % ''.join(lines)


#
# Extra Vars Rendering
#
class ExtraNamespace(object):
    '''
    Extra variables for the template namespace to pass to the renderer as named
    parameters.

    :param extras: dictionary of extra parameters. Defaults to an empty dict.
    '''
    def __init__(self, extras={}):
        self.namespace = dict(extras)

    def update(self, d):
        '''
        Updates the extra variable dictionary for the namespace.
        '''
        self.namespace.update(d)

    def make_ns(self, ns):
        '''
        Returns the `lazily` created template namespace.
        '''
        if self.namespace:
            val = {}
            val.update(self.namespace)
            val.update(ns)
            return val
        else:
            return ns


#
# Rendering Factory
#
class RendererFactory(object):
    '''
    Manufactures known Renderer objects.

    :param custom_renderers: custom-defined renderers to manufacture
    :param extra_vars: extra vars for the template namespace
    '''
    def __init__(self, custom_renderers={}, extra_vars={}):
        self._renderers = {}
        self._renderer_classes = dict(_builtin_renderers)
        self.add_renderers(custom_renderers)
        self.extra_vars = ExtraNamespace(extra_vars)

    def add_renderers(self, custom_dict):
        '''
        Adds a custom renderer.

        :param custom_dict: a dictionary of custom renderers to add
        '''
        self._renderer_classes.update(custom_dict)

    def available(self, name):
        '''
        Returns true if queried renderer class is available.

        :param name: renderer name
        '''
        return name in self._renderer_classes

    def get(self, name, template_path):
        '''
        Returns the renderer object.

        :param name: name of the requested renderer
        :param template_path: path to the template
        '''
        if name not in self._renderers:
            cls = self._renderer_classes.get(name)
            if cls is None:
                return None
            else:
                self._renderers[name] = cls(template_path, self.extra_vars)
        return self._renderers[name]
