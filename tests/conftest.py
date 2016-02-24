# -*- coding: utf-8 -*-
# :Project:  pyxc-pj -- test fixtures
# :Created:    lun 22 feb 2016 12:16:42 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
#
import ast
import inspect
import textwrap

import pytest

from pyxc.transforming import Transformer
from pj import transformations
from pj.js_ast import JSStatements

def ast_object(obj):
    src = inspect.getsource(obj)
    # ast wraps always into a module
    node = ast.parse(textwrap.dedent(src)).body[0]
    return node

def ast_dump_object(obj):
    node = ast_object(obj)
    return node, ast.dump(node)

def ast_object_to_js(obj):
    src = inspect.getsource(obj)
    node = ast.parse(textwrap.dedent(src))
    t = Transformer(transformations, JSStatements)
    return t.transform_code(node)

@pytest.fixture
def astdump():
    return ast_dump_object

@pytest.fixture
def astobj():
    return ast_object

@pytest.fixture
def astjs():
    return ast_object_to_js
