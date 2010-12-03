class ServerConfig(object):
    port = '8080'
    host = '0.0.0.0'
    threads = 1


class ApplicationConfig(object):
    root = None
    static_root = 'public'
    template_path= None
    debug= True


server = ServerConfig()
application = ApplicationConfig()

def import_runtime_conf(conf):
    if '.' in conf:
        parts = conf.split('.')
        name = '.'.join(parts[:-1])
        fromlist = parts[-1:]
    
    else:
        name = conf
        fromlist = []

    try:
        module = __import__(name, fromlist=fromlist)
        return getattr(module, parts[-1])
    except ImportError, e:
        raise ImportError('No module named %s' % conf)
    except AttributeError, e:
        raise ImportError('No module named %s' % conf)
