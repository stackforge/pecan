


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

