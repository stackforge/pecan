# Server Specific Configurations
server = {
    'port' : '8080',
    'host' : '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root' : None,
    'modules' : [],
    'static_root' : 'public', 
    'template_path' : '',
    'debug' : False,
    'force_canonical' : True,
    'errors' : {
        '__force_dict__' : True
    }
}

# Custom Configurations must be in Python dictionary format in user config
#
# foo = {'bar':'baz'}
# 
# All configurations are accessible at::
# pecan.conf
