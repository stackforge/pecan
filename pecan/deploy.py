from configuration import set_config, import_module, _runtime_conf as conf

def deploy(config_module_or_path):
    set_config(config_module_or_path)
    for module in getattr(conf.app, 'modules'):
        try:
            module_app = import_module('%s.app' % module.__name__)
            if hasattr(module_app, 'setup_app'):
                return module_app.setup_app(conf)
        except ImportError:
            continue

    raise Exception, 'No app.setup_app found in any of the configured app.modules'

