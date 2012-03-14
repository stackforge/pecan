import sys
from setuptools import setup, command, find_packages
from setuptools.command.test import test as TestCommand

version = '0.1.0'

#
# determine requirements
#
requirements = [
  "WebOb >= 1.0.0",
  "WebCore >= 1.0.0",
  "simplegeneric >= 0.7",
  "Mako >= 0.4.0",
  "Paste >= 1.7.5.1",
  "WebTest >= 1.2.2"
]

try:
    import json
except:
    try:
        import simplejson
    except:
        requirements.append("simplejson >= 2.1.1")

try:
    import argparse
except:
    requirements.append('argparse')

tests_require = requirements + ['virtualenv']
if sys.version_info < (2, 7):
    tests_require += ['unittest2']


class test(TestCommand):

    user_options = TestCommand.user_options + [(
        'functional',
        None,
        'Run all tests (even the really slow functional ones)'
    )]

    def initialize_options(self):
        self.functional = None
        return TestCommand.initialize_options(self)

    def finalize_options(self):
        if self.functional:
            import pecan
            setattr(pecan, '__run_all_tests__', True)
        return TestCommand.finalize_options(self)

#
# call setup
#
setup(
    name='pecan',
    version=version,
    description="A WSGI object-dispatching web framework, designed to be "\
                  "lean and fast, with few dependancies.",
    long_description=None,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ],
    keywords='web framework wsgi object-dispatch http',
    author='Jonathan LaCour, Ryan Petrello, Mark McClain, Yoann Roman, '\
           'Jeremy Jones, Alfredo Deza, Benjamin W. Smith',
    author_email='jonathan@cleverdevil.org',
    url='http://github.com/pecan/pecan',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    scripts=['bin/pecan'],
    zip_safe=False,
    install_requires=requirements,
    tests_require=tests_require,
    test_suite='pecan',
    cmdclass={'test': test},
    entry_points="""
    [pecan.command]
    serve = pecan.commands:ServeCommand
    shell = pecan.commands:ShellCommand
    create = pecan.commands:CreateCommand
    [console_scripts]
    pecan = pecan.commands:CommandRunner.handle_command_line
    """,
)
