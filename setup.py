# -*- coding: utf-8 -*-
# :Project:   metapensiero.pj -- A Python 3 to ES6 Javascript translator
# :Created:   lun 22 feb 2016 16:00:00 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: Copyright (C) 2016 Alberto Berti
#

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst'), encoding='utf-8') as f:
    CHANGES = f.read()
with open(os.path.join(here, 'version.txt'), encoding='utf-8') as f:
    VERSION = f.read().strip()

setup(
    name="javascripthon",
    version=VERSION,
    url="https://github.com/azazel75/metapensiero.pj",

    description="Javascript for refined palates:"
    " a Python 3 to ES6 Javascript translator",
    long_description=README + '\n\n' + CHANGES,

    author="Alberto Berti",
    author_email="alberto@arstecnica.it",

    license="GPLv3+",
    classifiers=[
        'Development Status :: 4 - Beta',
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
    keywords='JavaScript EcmaScript compilation translation transpiling babel',
    packages=['metapensiero.' + pkg
              for pkg in find_packages('src/metapensiero')],
    package_dir={'': 'src'},
    namespace_packages=['metapensiero',],
    install_requires=[
        'setuptools',
        'dukpy'
    ],
    extras_require={
        'dev': [
            'metapensiero.tool.bump_version',
            'readme_renderer',
        ],
        'test': [
            'pytest',
            'meta'
        ],
    },
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'javascripthon[test]'
    ],
    entry_points={
        'console_scripts': ['pj=metapensiero.pj.__main__:main'],
    },
    package_data={
        'metapensiero.pj': ['data/*.js']
    },
)
