from paste.script.templates import Template

DEFAULT_TEMPLATE = 'base'


class BaseTemplate(Template):
    summary = 'Template for creating a basic Pecan project'
    _template_dir = 'project'
    egg_plugins = ['Pecan']
