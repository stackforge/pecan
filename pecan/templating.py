import cgi

__all__ = ['RendererFactory']

_builtin_renderers = {}
error_formatters = []

#
# JSON rendering engine
#

class JsonRenderer(object):
    def __init__(self, path, extra_vars):
        pass
    
    def render(self, template_path, namespace):
        from jsonify import encode
        return encode(namespace)

_builtin_renderers['json'] = JsonRenderer


#
# Genshi rendering engine
# 

try:
    from genshi.template import (TemplateLoader,
                                TemplateError as gTemplateError)

    class GenshiRenderer(object):
        def __init__(self, path, extra_vars):
            self.loader = TemplateLoader([path], auto_reload=True)
            self.extra_vars = extra_vars
    
        def render(self, template_path, namespace):
            tmpl = self.loader.load(template_path)
            stream = tmpl.generate(**self.extra_vars.make_ns(namespace))
            return stream.render('html')

    _builtin_renderers['genshi'] = GenshiRenderer
 
    def format_genshi_error(exc_value):
        if isinstance(exc_value, (gTemplateError)):
            retval = '<h4>Genshi error %s</h4>' % cgi.escape(exc_value.message)
            retval += format_line_context(exc_value.filename, exc_value.lineno)
            return retval
    error_formatters.append(format_genshi_error)
except ImportError:                                 #pragma no cover
    pass


#
# Mako rendering engine
#

try:
    from mako.lookup import TemplateLookup
    from mako.exceptions import CompileException, SyntaxException, \
            html_error_template

    class MakoRenderer(object):
        def __init__(self, path, extra_vars):
            self.loader = TemplateLookup(directories=[path], output_encoding='utf-8')
            self.extra_vars = extra_vars
    
        def render(self, template_path, namespace):
            tmpl = self.loader.get_template(template_path)
            return tmpl.render(**self.extra_vars.make_ns(namespace))

    _builtin_renderers['mako'] = MakoRenderer

    def format_mako_error(exc_value):
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
        def __init__(self, path, extra_vars):
            self.loader = FileLoader(path, reload=True)
            self.extra_vars = extra_vars

        def render(self, template_path, namespace):
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
        def __init__(self, path, extra_vars):
            self.env = Environment(loader=FileSystemLoader(path))
            self.extra_vars = extra_vars

        def render(self, template_path, namespace):
            template = self.env.get_template(template_path)
            return template.render(self.extra_vars.make_ns(namespace))
    _builtin_renderers['jinja'] = JinjaRenderer

    def format_jinja_error(exc_value):
        if isinstance(exc_value, (jTemplateSyntaxError)):
            retval = '<h4>Jinja2 template syntax error in \'%s\' on line %d</h4><div>%s</div>' % (exc_value.name, exc_value.lineno, exc_value.message)
            retval += format_line_context(exc_value.filename, exc_value.lineno)
            return retval
    error_formatters.append(format_jinja_error)
except ImportError:                                 # pragma no cover
    pass

#
# format helper function
#
def format_line_context(filename, lineno, context=10):
    lines = open(filename).readlines()

    lineno = lineno - 1 # files are indexed by 1 not 0
    if lineno > 0:
        start_lineno = max(lineno-context, 0)
        end_lineno = lineno+context

        lines = [cgi.escape(l) for l in lines[start_lineno:end_lineno]]
        i = lineno-start_lineno
        lines[i] = '<strong>%s</strong>' % lines[i]

    else:
        lines = [cgi.escape(l) for l in lines[:context]]

    return '<pre style="background-color:#ccc;padding:2em;">%s</pre>' % ''.join(lines)

#
# Extra Vars Rendering 
#
class ExtraNamespace(object):
    def __init__(self, extras={}):
        self.namespace = dict(extras)

    def update(self, d):
        self.namespace.update(d)

    def make_ns(self, ns):
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
    def __init__(self, custom_renderers={}, extra_vars={}):
        self._renderers = {}
        self._renderer_classes = dict(_builtin_renderers)
        self.add_renderers(custom_renderers)
        self.extra_vars = ExtraNamespace(extra_vars)

    def add_renderers(self, custom_dict):
        self._renderer_classes.update(custom_dict)

    def available(self, name):
        return name in self._renderer_classes

    def get(self, name, template_path):
        if name not in self._renderers:
            cls = self._renderer_classes.get(name)
            if cls is None:
                return None
            else:
                self._renderers[name] = cls(template_path, self.extra_vars)
        return self._renderers[name]
