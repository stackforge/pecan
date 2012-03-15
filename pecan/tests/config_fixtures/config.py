

# Server Specific Configurations
server = {
    'port': '8081',
    'host': '1.1.1.1',
    'hostport': '{pecan.conf.server.host}:{pecan.conf.server.port}'
}

# Pecan Application Configurations
app = {
    'static_root': 'public',
    'template_path': 'myproject/templates',
    'debug': True
}

# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
#
# All configurations are accessible at::
# pecan.conf
