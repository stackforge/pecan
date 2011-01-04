__all__ = ['RendererFactory']

_builtin_renderers = {}

#
# JSON rendering engine
#

class JsonRenderer(object):
    content_type = 'application/json'
    
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
        content_type = 'text/html'

        def __init__(self, path, extra_vars):
            self.loader = TemplateLoader([path], auto_reload=True)
            self.extra_vars = extra_vars
    
        def render(self, template_path, namespace):
            tmpl = self.loader.load(template_path)
            stream = tmpl.generate(**self.extra_vars.make_ns(namespace))
            return stream.render('html')

    _builtin_renderers['genshi'] = GenshiRenderer
except ImportError:                                 #pragma no cover
    pass


#
# Mako rendering engine
#

try:
    from mako.lookup import TemplateLookup

    class MakoRenderer(object):
        content_type = 'text/html'

        def __init__(self, path, extra_vars):
            self.loader = TemplateLookup(directories=[path])
            self.extra_vars = extra_vars
    
        def render(self, template_path, namespace):
            tmpl = self.loader.get_template(template_path)
            return tmpl.render(**self.extra_vars.make_ns(namespace))

    _builtin_renderers['mako'] = MakoRenderer
except ImportError:                                 # pragma no cover
    pass


#
# Kajiki rendering engine
#

try:
    from kajiki.loader import FileLoader

    class KajikiRenderer(object):
        content_type = 'text/html'
    
        def __init__(self, path, extra_vars):
            self.loader = FileLoader(path, reload=True)
            self.extra_vars = extra_vars

        def render(self, template_path, namespace):
            Template = self.loader.import_(template_path)
            stream = Template(self.extra_vars.make_ns(namespace))
            return stream.render()
    _builtin_renderers['kajiki'] = KajikiRenderer
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
            retval = {}
            retval.update(self.namespace)
            retval.update(ns)
            return retval
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

    def create(self, name, template_path):
        cls = self._renderer_classes.get(name)

        if cls is None:
            return None
        else:
            return cls(template_path, self.extra_vars)
        
    def get(self, name, template_path):
        key = name+template_path
        if key not in self._renderers:
            self._renderers[key] = self.create(name, template_path)
        return self._renderers[key]
