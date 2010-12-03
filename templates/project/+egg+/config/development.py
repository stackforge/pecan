from ${egg}.controllers.root import RootController
from pecan.configuration import server, application 


# Server Specific Configurations
server.port = '8080'
server.host = '0.0.0.0'

# Pecan Application Configurations
application.root = RootController()
application.static_root = 'public' 
application.template_path = 'test_conf/templates'
application.debug = True 

