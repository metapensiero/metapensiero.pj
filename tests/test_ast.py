# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj -- tests
# :Created:  lun 22 feb 2016 12:50:26 CET
# :Author:   Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import pytest

from conftest import load_tests_from_directory


@pytest.mark.parametrize('name, py_code,js_src',
                         load_tests_from_directory('test_ast_dump', '.ast'))
def test_ast_dump(name, py_code, js_src, astdump):
    node, dump = astdump(py_code)
    dump = '\n'.join(line.rstrip() for line in dump.splitlines()).rstrip()
    assert dump == js_src.rstrip()


@pytest.mark.parametrize('name, py_code,js_src',
                         load_tests_from_directory('test_ast_dump_first', '.ast'))
def test_ast_dump_first(name, py_code, js_src, astdump):
    node, dump = astdump(py_code, first_stmt_only=True)
    dump = '\n'.join(line.rstrip() for line in dump.splitlines()).rstrip()
    assert dump == js_src.rstrip()


@pytest.mark.parametrize('name, py_code,js_src',
                         load_tests_from_directory('test_ast_es6'))
def test_ast_es6(name, py_code, js_src, astjs):
    dump = str(astjs(py_code, es6=True))
    dump = '\n'.join(line.rstrip() for line in dump.splitlines()).rstrip()
    assert dump == js_src.rstrip()
