


class PecanConfig(object):
    """Base configuration object for Pecan. It provides 
    settings that can be overriden."""

    port    = '8080'
    host    = '0.0.0.0'
    threads = 1



def _find_config(name):
    for config in _sub_classes():
        if name == config.__name__:
            return config


def _sub_classes():
    return PecanConfig.__subclasses__()


