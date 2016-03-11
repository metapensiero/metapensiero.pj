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

from metapensiero.pj.processor.transforming import Transformer
from metapensiero.pj import transformations
from metapensiero.pj.js_ast import JSStatements

def ast_object(obj):
    src = inspect.getsource(obj)
    # ast wraps always into a module
    node = ast.parse(textwrap.dedent(src)).body[0]
    return node

def ast_dump_object(obj):
    from meta.asttools import str_ast
    node = ast_object(obj)
    return node, str_ast(node)

def ast_object_to_js(obj, es6=False):
    src = inspect.getsource(obj)
    node = ast.parse(textwrap.dedent(src))
    t = Transformer(transformations, JSStatements, es6=es6)
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
