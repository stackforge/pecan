import sys
import pkg_resources
import inspect
import logging

log = logging.getLogger(__name__)


class PecanExtensionMissing(ImportError):
    pass


class PecanExtensionImporter(object):
    """
    Short circuits imports for extensions.

    This is used in combination with ``pecan.ext`` so that when a user does
    ``from pecan.ext import foo``, it will attempt to map ``foo`` to a
    registered setuptools entry point in some other (Pecan extension) project.

    Conversely, an extension developer may define an entry point in his
    ``setup.py``, e.g.,

    setup(
      ...
      entry_points='''
      [pecan.extension]
      celery = pecancelery.lib.core
      '''
    )

    This is mostly for convenience and consistency.  In this way, Pecan can
    maintain an ecosystem of extensions that share a common namespace,
    ``pecan.ext``, while still maintaining backwards compatibility for simple
    package names (e.g., ``pecancelery``).
    """

    extension_module = 'pecan.ext'
    prefix = extension_module + '.'

    def install(self):
        if self not in sys.meta_path:
            sys.meta_path.append(self)

    def __eq__(self, b):
        return self.__class__.__module__ == b.__class__.__module__ and \
            self.__class__.__name__ == b.__class__.__name__

    def __ne__(self, b):
        return not self.__eq__(b)

    def find_module(self, fullname, path=None):
        if fullname.startswith(self.prefix):
            return self

    def load_module(self, fullname):
        if fullname in sys.modules:
            return self
        extname = fullname.split(self.prefix)[1]
        module = self.find_module_for_extension(extname)
        realname = module.__name__
        try:
            __import__(realname)
        except ImportError:
            raise sys.exc_info()
        module = sys.modules[fullname] = sys.modules[realname]
        if '.' not in extname:
            setattr(sys.modules[self.extension_module], extname, module)
        return module

    def find_module_for_extension(self, name):
        for ep in pkg_resources.iter_entry_points('pecan.extension'):
            if ep.name != name:
                continue
            log.debug('%s loading extension %s', self.__class__.__name__, ep)
            module = ep.load()
            if not inspect.ismodule(module):
                log.debug('%s is not a module, skipping...' % module)
                continue
            return module
        raise PecanExtensionMissing(
            'The `pecan.ext.%s` extension is not installed.' % name
        )
