# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj -- common transformation functions
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
#            Devan Lai <devan.lai@gmail.com>
# :License:  GNU General Public License version 3 or later
#

import ast
from functools import reduce

from macropy.core.quotes import macros, ast_literal, ast_list, q, name
from macropy.experimental.pattern import macros, switch  # noqa: F811,F401


from ..js_ast import (
    JSBinOp,
    JSMultipleArgsOp,
    JSName,
    JSOpInstanceof,
    JSOpOr,
    JSOpStrongEq,
    JSOpTypeof,
    JSStr,
    JSUnaryOp,
)


def _build_call_isinstance(tgt, cls_or_seq):
    """Helper to build the translate the equivalence of ``isinstance(foo, Bar)``
    to ``foo instanceof Bar`` and ``isinstance(Foo, (Bar, Zoo))`` to
    ``foo instanceof Bar || foo instanceof Zoo``.
    """
    with switch(cls_or_seq):
        if (ast.Tuple(elts=classes) | ast.List(elts=classes) |  # noqa: F821
            ast.Set(elts=classes)):  # noqa: E129,F821
            binops = [q[isinstance(ast_literal[tgt], ast_literal[c])]
                      for c in classes]  # noqa: F821
            return ast.BoolOp(op=ast.Or(), values=binops)
        elif q[str]:
            return q[typeof(ast_literal[tgt]) == 'string' or  # noqa: F821
                     isinstance(ast_literal[tgt], String)]  # noqa: F821
        elif q[int] | q[float]:
            return q[typeof(ast_literal[tgt]) == 'number' or  # noqa: F821
                     isinstance(ast_literal[tgt], Number)]  # noqa: F821
        else:
            return JSBinOp(tgt, JSOpInstanceof(), cls_or_seq)
