def setup_app(config):
    assert config.foo.sample_key == True
    return 'DEPLOYED!'
