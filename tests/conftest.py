# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj -- test fixtures
# :Created:  lun 22 feb 2016 12:16:42 CET
# :Authors:  Alberto Berti <alberto@metapensiero.it>,
#            Lele Gaifax <lele@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

from glob import glob
from os.path import dirname, exists, isabs, isdir, join, split, splitext
import sys

import pytest

from metapensiero.pj.testing import (ast_object, ast_dump_object,
                                     ast_object_to_js)


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
                        raise ValueError('Bad header, expected "## value:'
                                         ' expression",'
                                         ' got: %s' % line.rstrip())
                    option = option.strip()
                    expr = expr.strip()
                    value = eval(expr, {'python_version': sys.version_info})
                    if option == 'requires':
                        if not value:
                            return None, None, 'Requires %s' % expr
                    else:
                        options[option] = value
                else:
                    script.append(line)
    py_src = ''.join(script)
    py_code = compile(py_src, filename, 'exec')
    return py_code, py_src, options


def load_tests_from_directory(dir, ext=None):
    ext = ext or '.out'
    if not isabs(dir):
        dir = join(dirname(__file__), dir)
    if not isdir(dir):
        raise RuntimeError('%s does not exist or is not a directory' % dir)
    for pyfile in sorted(glob(join(dir, '*.py'))):
        py_code, py_src, options = load_python_code(pyfile)
        if py_code is None:
            yield pytest.mark.skip((split(pyfile)[1],
                                    None, None, None, None))(reason=options)
            continue

        cmpfile = splitext(pyfile)[0] + ext
        if exists(cmpfile):
            with open(cmpfile, encoding='utf-8') as f:
                expected = f.read()
            # The first item is to make it easier to spot the right test
            # in verbose mode
            yield split(pyfile)[1], py_code, py_src, options, expected
        else:
            raise RuntimeError('%s has no correspondent %s' % (
                pyfile, cmpfile))


def pytest_generate_tests(metafunc):
    if metafunc.cls is not None and metafunc.cls.__name__.endswith('FS'):
        ext = getattr(metafunc.cls, 'EXT', None)
        if isinstance(ext, dict):
            ext = ext[metafunc.function.__name__]
        moddir = splitext(metafunc.module.__file__)[0]
        testdir = join(moddir, metafunc.function.__name__)
        argvalues = list(load_tests_from_directory(testdir, ext))
        metafunc.parametrize(
            ('name', 'py_code', 'py_src', 'options', 'expected'), argvalues,
            ids=[v[0] if isinstance(v, tuple)
                 else v.args[0][0] for v in argvalues])
