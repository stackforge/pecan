import sys

from setuptools import setup, find_packages

version = '0.4.5'

#
# determine requirements
#
with open('requirements.txt') as reqs:
    requirements = [
        line for line in reqs.read().split('\n')
        if (line and not line.startswith('-'))
    ]

try:
    import json  # noqa
except:
    try:
        import simplejson  # noqa
    except:
        requirements.append("simplejson >= 2.1.1")

try:
    from logging.config import dictConfig  # noqa
except ImportError:
    #
    # This was introduced in Python 2.7 - the logutils package contains
    # a backported replacement for 2.6
    #
    requirements.append('logutils')

try:
    import argparse  # noqa
except:
    #
    # This was introduced in Python 2.7 - the argparse package contains
    # a backported replacement for 2.6
    #
    requirements.append('argparse')

try:
    from functools import singledispatch  # noqa
except:
    #
    # This was introduced in Python 3.4 - the singledispatch package contains
    # a backported replacement for 2.6 through 3.4
    #
    requirements.append('singledispatch')


tests_require = requirements + [
    'virtualenv',
    'gunicorn',
    'mock',
    'sqlalchemy'
]
if sys.version_info < (2, 7):
    tests_require += ['unittest2']

if sys.version_info < (3, 0):
    # These don't support Python3 yet - don't run their tests
    tests_require += ['Kajiki']
    tests_require += ['Genshi']
else:
    # Genshi added Python3 support in 0.7
    tests_require += ['Genshi>=0.7']

if sys.version_info < (3, 0) or sys.version_info >= (3, 3):
    tests_require += ['Jinja2']

#
# call setup
#
setup(
    name='pecan',
    version=version,
    description="A WSGI object-dispatching web framework, designed to be "
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ],
    keywords='web framework wsgi object-dispatch http',
    author='Jonathan LaCour',
    author_email='info@pecanpy.org',
    url='http://github.com/stackforge/pecan',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    scripts=['bin/pecan'],
    zip_safe=False,
    install_requires=requirements,
    tests_require=tests_require,
    test_suite='pecan',
    entry_points="""
    [pecan.command]
    serve = pecan.commands:ServeCommand
    shell = pecan.commands:ShellCommand
    create = pecan.commands:CreateCommand
    [pecan.scaffold]
    base = pecan.scaffolds:BaseScaffold
    [console_scripts]
    pecan = pecan.commands:CommandRunner.handle_command_line
    gunicorn_pecan = pecan.commands.serve:gunicorn_run
    """
)
