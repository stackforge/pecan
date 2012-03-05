from pecan.util import compat_splitext

def test_compat_splitext():
    assert ('foo', '.bar') == compat_splitext('foo.bar')
    assert ('/foo/bar', '.txt') == compat_splitext('/foo/bar.txt')
    assert ('/foo/bar', '') == compat_splitext('/foo/bar')
    assert ('.bashrc', '') == compat_splitext('.bashrc')
    assert ('..bashrc', '') == compat_splitext('..bashrc')
    assert ('/.bashrc', '') == compat_splitext('/.bashrc')
    assert ('/foo.bar/.bashrc', '') == compat_splitext('/foo.bar/.bashrc')
    assert ('/foo.js', '.js') == compat_splitext('/foo.js.js')
