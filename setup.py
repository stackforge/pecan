from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name                 = 'pecan',
    version              = version,
    description          = "A WSGI object-dispatching web framework, in the spirit of TurboGears, only much much smaller, with many fewer dependancies.",
    long_description     = None,
    classifiers          = [],
    keywords             = '',
    author               = 'Jonathan LaCour',
    author_email         = 'jonathan@cleverdevil.org',
    url                  = 'http://sf.net/p/pecan',
    license              = 'BSD',
    packages             = find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data = True,
    zip_safe             = True,
    install_requires=[
      "WebOb >= 0.9.8", 
      "simplejson >= 2.0.9",
      "simplegeneric >= 0.7",
      "Genshi >= 0.6",
      "Kajiki >= 0.2.2",
      "Mako >= 0.3",
      "py >= 1.3.4",
      "WebTest >= 1.2.2"
    ],
    entry_points = """
    # -*- Entry points: -*-
    """,
)
