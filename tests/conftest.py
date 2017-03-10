# -*- coding: utf-8 -*-
# :Project: pyxc-pj -- test fixtures
# :Created: lun 22 feb 2016 12:16:42 CET
# :Author:  Alberto Berti <alberto@metapensiero.it>
# :License: GNU General Public License version 3 or later
#

from glob import glob
from os.path import dirname, exists, isabs, isdir, join, split, splitext

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


def load_tests_from_directory(dir, ext=None):
    ext = ext or '.js'
    if not isabs(dir):
        dir = join(dirname(__file__), dir)
    if not isdir(dir):
        raise RuntimeError('%s does not exist or is not a directory' % dir)
    for pyfile in glob(join(dir, '*.py')):
        cmpfile = splitext(pyfile)[0] + ext
        if exists(cmpfile):
            with open(pyfile, encoding='utf-8') as f:
                pysrc = f.read()
            pycode = compile(pysrc, pyfile, 'exec')
            with open(cmpfile, encoding='utf-8') as f:
                cmpsrc = f.read()
            # The first item is to make it easier to spot the right test
            # in verbose mode
            yield split(pyfile)[1], pycode, cmpsrc
        else:
            raise RuntimeError('%s has no correspondent %s' % (pyfile, cmpfile))
