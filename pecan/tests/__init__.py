__all__ = ['collector']

def collector():
    try:
        from unittest import TestLoader
        assert hasattr(TestLoader, 'discover')
        return TestLoader().discover('pecan.tests')
    except:
        import unittest2
        return unittest2.collector
