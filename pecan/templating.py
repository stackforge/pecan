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
    from genshi.template import TemplateLoader

    class GenshiRenderer(object):
        def __init__(self, path, extra_vars):
            self.loader = TemplateLoader([path], auto_reload=True)
            self.extra_vars = extra_vars
    
        def render(self, template_path, namespace):
            tmpl = self.loader.load(template_path)
            stream = tmpl.generate(**self.extra_vars.make_ns(namespace))
            return stream.render('html')

    _builtin_renderers['genshi'] = GenshiRenderer
    # TODO: add error formatter for genshi
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
            self.loader = TemplateLookup(directories=[path])
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
