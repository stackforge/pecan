__all__ = ['renderers']

_renderers = {}

class RendererFactory(object):
    def create(self, name, template_path):
        if name == 'genshi':
            return GenshiRenderer(template_path)
        elif name == 'kajiki':
            return KajikiRenderer(template_path)
        elif name == 'mako':
            return MakoRenderer(template_path)
        elif name == 'json':
            return JsonRenderer(template_path)
        
    def get(self, name, template_path):
        key = name+template_path
        if key not in _renderers:
            _renderers[key] = self.create(name, template_path)
        return _renderers[key]

renderers = RendererFactory()
            

#
# JSON rendering engine
#

class JsonRenderer(object):
    content_type = 'application/json'
    
    def __init__(self, path):
        pass
    
    def render(self, template_path, namespace):
        from jsonify import encode
        result = encode(namespace)
        return result


#
# Genshi rendering engine
# 

class GenshiRenderer(object):
    content_type = 'text/html'

    def __init__(self, path):
        from genshi.template import TemplateLoader
        self.loader = TemplateLoader([path], auto_reload=True)
    
    def render(self, template_path, namespace):
        tmpl = self.loader.load(template_path)
        stream = tmpl.generate(**namespace)
        return stream.render('html')


#
# Mako rendering engine
#

class MakoRenderer(object):
    content_type = 'text/html'

    def __init__(self, path):
        from mako.lookup import TemplateLookup
        self.loader = TemplateLookup(directories=[path])
    
    def render(self, template_path, namespace):
        tmpl = self.loader.get_template(template_path)
        return tmpl.render(**namespace)


#
# Kajiki rendering engine
#

class KajikiRenderer(object):
    content_type = 'text/html'

    def __init__(self, path):
        from kajiki.loader import FileLoader
        self.loader = FileLoader(path, reload=True)

    def render(self, template_path, namespace):
        Template = self.loader.import_(template_path)
        stream = Template(namespace)
        return stream.render()