from pecan import load_app
from webtest import TestApp

def load_test_app(config):
    return TestApp(load_app(config))
