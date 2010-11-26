from setuptools import setup, Command, find_packages

version = '0.1'

#
# integration with py.test for `python setup.py test`
#
tests_require = [
  "py == 1.3.4",
  "WebTest == 1.2.2",
]

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import py
        py.cmdline.pytest(py.std.sys.argv[2:])


#
# determine requirements
#
requirements = [
  "WebOb == 1.0.0", 
  "WebCore == 1.0.0",
  "simplegeneric == 0.7",
  "Kajiki == 0.3.1",
  "Paste == 1.7.5.1",
  "PasteScript == 1.7.3",
  "formencode == 1.2.2"
]

try:
    import json
except:
    requirements.append("simplejson == 2.1.1")


#
# call setup
#
setup(
    name                 = 'pecan',
    version              = version,
    description          = "A WSGI object-dispatching web framework, in the spirit of TurboGears, only much much smaller, with many fewer dependencies.",
    long_description     = None,
    classifiers          = [],
    keywords             = '',
    author               = 'Jonathan LaCour',
    author_email         = 'jonathan@cleverdevil.org',
    url                  = 'http://github.com/cleverdevil/pecan',
    license              = 'BSD',
    packages             = find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data = True,
    zip_safe             = True,
    cmdclass             = {'test': PyTest},
    install_requires     = requirements,
    entry_points         = """
    [paste.paster_create_template]
    pecan-base = templates:NewProjectTemplate
    """,
)
