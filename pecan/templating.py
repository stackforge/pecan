__all__ = ['renderers']


#
# JSON rendering engine
#

class JsonRenderer(object):
    content_type = 'application/json'
    
    def __init__(self, path, context):
        pass
    
    def render(self, template_path, namespace):
        from jsonify import encode
        return encode(namespace)


#
# Genshi rendering engine
# 

class GenshiRenderer(object):
    content_type = 'text/html'

    def __init__(self, path, context):
        from genshi.template import TemplateLoader
        self.loader = TemplateLoader([path], auto_reload=True)
        self.context = context
    
    def render(self, template_path, namespace):
        tmpl = self.loader.load(template_path)
        stream = tmpl.generate(**self.context.make_ns(namespace))
        return stream.render('html')


#
# Mako rendering engine
#

class MakoRenderer(object):
    content_type = 'text/html'

    def __init__(self, path, context):
        from mako.lookup import TemplateLookup
        self.loader = TemplateLookup(directories=[path])
        self.context = context
    
    def render(self, template_path, namespace):
        tmpl = self.loader.get_template(template_path)
        return tmpl.render(**self.context.make_ns(namespace))


#
# Kajiki rendering engine
#

class KajikiRenderer(object):
    content_type = 'text/html'

    def __init__(self, path, context):
        from kajiki.loader import FileLoader
        self.loader = FileLoader(path, reload=True)
        self.context = context

    def render(self, template_path, namespace):
        Template = self.loader.import_(template_path)
        stream = Template(self.context.make_ns(namespace))
        return stream.render()

#
# Rendering Context
#
class RenderingContext(object):
    def __init__(self, globals={}):
        self.namespace = dict(globals)

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
    def __init__(self, custom_renderers={}, extra_namespace={}):
        self._renderers = {}
        self._renderer_classes = {
            'genshi': GenshiRenderer,
            'kajiki': KajikiRenderer,
            'mako'  : MakoRenderer,
            'json'  : JsonRenderer
        }

        self.add_renderers(custom_renderers)
        self.context = RenderingContext(extra_namespace)

    def add_renderers(self, custom_dict):
        self._renderer_classes.update(custom_dict)

    def create(self, name, template_path):
        cls = self._renderer_classes.get(name)

        if cls is None:
            return None
        else:
            return cls(template_path, self.context)
        
    def get(self, name, template_path):
        key = name+template_path
        if key not in self._renderers:
            self._renderers[key] = self.create(name, template_path)
        return self._renderers[key]
