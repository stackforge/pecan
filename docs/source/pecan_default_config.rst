.. _pecan_default_config:

:mod:`pecan.default_config` -- Pecan Default Configuration
==========================================================

The :mod:`pecan.default_config` module contains the default configuration
for all Pecan applications.

.. automodule:: pecan.default_config
  :members:
  :show-inheritance:

The default configuration is as follows::

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