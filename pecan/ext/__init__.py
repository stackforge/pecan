def install():
    from pecan.extensions import PecanExtensionImporter
    PecanExtensionImporter().install()

install()
del install
