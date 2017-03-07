# -*- coding: utf-8 -*-
# :Project: pyxc-pj -- test fixtures
# :Created: lun 22 feb 2016 12:16:42 CET
# :Author:  Alberto Berti <alberto@metapensiero.it>
# :License: GNU General Public License version 3 or later
#

import pathlib

import pytest
from metapensiero.pj.testing import ast_object, ast_dump_object, ast_object_to_js

@pytest.fixture
def astdump():
    return ast_dump_object


@pytest.fixture
def astobj():
    return ast_object


@pytest.fixture
def astjs():
    return ast_object_to_js


def load_tests_from_directory(dir):
    base = pathlib.Path(dir)
    if not base.is_absolute():
        base = pathlib.Path(__file__).parent / base
    for pyfile in base.glob('*.py'):
        jsfile = pyfile.with_suffix('.js')
        if jsfile.exists():
            pysrc = pyfile.read_text()
            pycode = compile(pysrc, pyfile, 'exec')
            # The first item is to make it easier to spot the right test
            # in verbose mode
            yield pyfile.stem, pycode, jsfile.read_text()
        else:
            raise RuntimeError('%s has no correspondent %s' % (pyfile, jsfile))
