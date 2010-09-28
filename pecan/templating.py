renderers = {}


#
# JSON rendering engine
#

class JsonRenderer(object):
    content_type = 'application/json'
    
    def render(self, template_path, namespace):
        from jsonify import encode
        return encode(namespace)

renderers['json'] = JsonRenderer()


#
# Genshi rendering engine
# 

try:
    from genshi.template import TemplateLoader
    
    class GenshiRenderer(object):
        content_type = 'text/html'
    
        def __init__(self):
            self.loader = TemplateLoader(['templates'], auto_reload=True)
                                
        def render(self, template_path, namespace):
            tmpl = self.loader.load(template_path)
            stream = tmpl.generate(**namespace)
            return stream.render('html')
except ImportError:
    pass
else:
    renderers['genshi'] = GenshiRenderer()


#
# Mako rendering engine
#

try:
    from mako.lookup import TemplateLookup
    class MakoRenderer(object):
        content_type = 'text/html'
    
        def __init__(self):
            self.loader = TemplateLookup(directories=['templates'])
    
        def render(self, template_path, namespace):
            tmpl = self.loader.get_template(template_path)
            return tmpl.render(**namespace)
except ImportError:
    pass
else:
    renderers['mako'] = MakoRenderer()
    

#
# Kajiki rendering engine
# 

try:
    from kajiki.loader import FileLoader

    class KajikiRenderer(object):
        content_type = 'text/html'

        def __init__(self):
            self.loader = FileLoader('templates', reload=True)

        def render(self, template_path, namespace):
            Template = self.loader.import_(template_path)
            stream = Template(namespace)
            return stream.render()
except ImportError:
    pass
else:
    renderers['kajiki'] = KajikiRenderer()