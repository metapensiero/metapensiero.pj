# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj -- test utilities
# :Created:  mer 09 nov 2016 20:32:09 CET
# :Author:   Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast
import inspect
import textwrap

from . import transformations
from .js_ast import JSStatements
from .processor.transforming import Transformer


def ast_object(obj):
    """Convert a Python object to its AST representation."""
    src = inspect.getsource(obj)
    # ast wraps always into a module
    node = ast.parse(textwrap.dedent(src)).body[0]
    return node


def ast_dump_object(obj, first_stmt_only=False):
    """Convert a Python object to its AST representation and the serialization of
    this to a string, optionally serializing the first element in its body.
    """
    from meta.asttools import str_ast
    node = ast_object(obj)
    if first_stmt_only:
        node = node.body[0]
    return node, str_ast(node)


def ast_object_to_js(obj, es6=False):
    """Convert a Python object to JS using pj, optionally transforming
    with ES6 features enabled.
    """
    src = inspect.getsource(obj)
    node = ast.parse(textwrap.dedent(src))
    t = Transformer(transformations, JSStatements, es6=es6)
    return t.transform_code(node)


def ast_dump_file(fname):
    """Dump an entire file."""
    with open(fname) as f:
        return ast_dumps(f.read(), filename=fname)


def ast_dumps(input, filename='', first_stmt_only=False):
    """AST dump a string."""
    try:
        from meta.asttools import str_ast
    except ImportError:
        str_ast = None
    node = ast.parse(input, filename=filename)
    if first_stmt_only:
        node = node.body[0]
    if str_ast:
        dump = str_ast(node)
    else:
        dump = ""
    return node, dump
