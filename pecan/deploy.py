from .core import load_app


def deploy(config):
    """
    Given a config (dictionary of relative filename), returns a configured
    WSGI app.
    """
    return load_app(config)
