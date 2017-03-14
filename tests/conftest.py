# -*- coding: utf-8 -*-
# :Project: pyxc-pj -- test fixtures
# :Created: lun 22 feb 2016 12:16:42 CET
# :Author:  Alberto Berti <alberto@metapensiero.it>
# :License: GNU General Public License version 3 or later
#

from glob import glob
from os.path import dirname, exists, isabs, isdir, join, split, splitext
import sys

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


def load_python_code(filename):
    options = {}
    script = []
    with open(filename, encoding='utf-8') as f:
        for line in f.readlines():
            if script:
                script.append(line)
            else:
                if line.startswith('##'):
                    try:
                        option, expr = line.strip().lstrip('# ').split(':', 1)
                    except:
                        raise ValueError('Bad header, expected "## value: expression",'
                                         ' got: %s' % line.rstrip())
                    option = option.strip()
                    value = eval(expr.strip(), {
                        'python_version': sys.version_info
                    })
                    if option == 'requires':
                        if not value:
                            return None, expr
                    else:
                        options[option] = value
                else:
                    script.append(line)
    py_code = compile(''.join(script), filename, 'exec')
    return py_code, options


def load_tests_from_directory(dir):
    if not isabs(dir):
        dir = join(dirname(__file__), dir)
    if not isdir(dir):
        raise RuntimeError('%s does not exist or is not a directory' % dir)
    for pyfile in sorted(glob(join(dir, '*.py'))):
        py_code, options = load_python_code(pyfile)
        if py_code is None:
            # TODO: it would be nice to report this as an XFail
            continue
        cmpfile = splitext(pyfile)[0] + '.out'
        if exists(cmpfile):
            with open(cmpfile, encoding='utf-8') as f:
                expected = f.read()
            # The first item is to make it easier to spot the right test
            # in verbose mode
            yield split(pyfile)[1], py_code, options, expected
        else:
            raise RuntimeError('%s has no correspondent %s' % (pyfile, cmpfile))


def pytest_make_parametrize_id(config, val):
    return val[0]


def pytest_generate_tests(metafunc):
    if 'fstest' in metafunc.fixturenames:
        moddir = splitext(metafunc.module.__file__)[0]
        testdir = join(moddir, metafunc.function.__name__)
        metafunc.parametrize("fstest",
                             load_tests_from_directory(testdir))
