# -*- coding: utf-8 -*-
# :Project:   metapensiero.pj -- matching helpers
# :Created:   sab 17 feb 2018 13:08:58 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Alberto Berti
#

import ast

from macropy.core import ast_repr, Literal
from macropy.core.macros import Macros, macro_stub, check_annotated
from macropy.core.quotes import macros, ast_literal, unquote_search
from macropy.core.hquotes import macros, hq  # noqa F811
from macropy.core.walkers import Walker
from macropy.experimental.pattern import macros, build_matcher  # noqa F811


macros = Macros()  # noqa F811


@Walker
def value_search(tree, match_ctx, **kw):
    "Get the values from the helper stubs."
    res = check_annotated(tree)  # returns something if tree == 'foo[...]'
    if res:
        func, right = res
        for f in [value]:
            if f.__name__ == func:
                return f(right, match_ctx)


@macro_stub
def value(tree, match_ctx):
    return Literal(tree)


@macros.expr
def m(tree, **kw):
    """It's almost identical to a quasiquote, redefined to give better
    visibility to the ``ast.Name``s used to mark var names."""
    vars = set()
    ex = unquote_search.recurse(tree)
    ex = value_search.recurse(ex, match_ctx=None)
    ex = ast_repr(ex)
    matcher = build_matcher(ex, vars)
    return hq[lambda tree: (ast_literal[matcher]).match(tree)]
