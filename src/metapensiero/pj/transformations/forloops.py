# -*- coding: utf-8 -*-
# :Project:  pj -- for loops transformations
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast

from ..js_ast import *


def For_range(t, x):
    """Special conversion for ``for name in range(n)``, which detects
    ``range()`` calls and convert the statement to:

    .. code:: javascript

      for (var name = 0, __bound = bound; name < __bound; name++) {
          // ...
      }

    """
    if (isinstance(x.target, ast.Name) and
        isinstance(x.iter, ast.Call) and
        isinstance(x.iter.func, ast.Name) and
        x.iter.func.id == 'range' and
        len(x.iter.args) in [1, 2]) and (not x.orelse):

        name = x.target
        body = x.body
        if len(x.iter.args) == 1:
            start = JSNum(0)
            bound = x.iter.args[0]
        else:
            start = x.iter.args[0]
            bound = x.iter.args[1]

        __bound = t.new_name()

        return JSForStatement(
            JSVarStatement(
                [name.id, __bound],
                [start, bound]),
            JSBinOp(JSName(name.id), JSOpLt(), JSName(__bound)),
            JSAugAssignStatement(
                JSName(name.id), JSOpAdd(), JSNum(1)),
            body
        )

def For_dict(t, x):
    """Special 'for name in dict(expr)' statement translation. It detects
    the ``dict()`` call and converts it to:

    .. code:: javascript

      var __dict = expr;
      for (var name in __dict) {
          if (__dict.hasOwnProperty(name)) {
          // ...
          }
      }
    """
    if (isinstance(x.iter, ast.Call) and
        isinstance(x.iter.func, ast.Name) and
        x.iter.func.id == 'dict' and
        len(x.iter.args) == 1) and (not x.orelse):

        t.unsupported(x, not isinstance(x.target, ast.Name),
                      "Target must be a name")

        name = x.target
        expr = x.iter.args[0]
        body = x.body

        __dict = t.new_name()

        return JSStatements([
            JSVarStatement([__dict], [expr]),
            JSForeachStatement(
                name.id,
                JSName(__dict),
                [
                    JSIfStatement(
                        JSCall(
                            JSAttribute(JSName(__dict), 'hasOwnProperty'),
                            [JSName(name.id)]
                        ),
                        body, None
                    )
                ]
            )
        ])


def For_default(t, x):
    """Assumes that the iteration is over a list.
    Converts something like:

    .. code:: python

      for name in expr:
          #body...

    to:

    .. code:: javascript

      for(var name, __list=expr, __i=0, __bound=__list.length; __i < __bound: __i++) {
          name = __list[__i];
          //body ...
      }

    """

    t.unsupported(x, not isinstance(x.target, ast.Name), "Target must be a name")

    name = x.target
    expr = x.iter
    body = x.body

    __list = t.new_name()
    __bound = t.new_name()
    __i = t.new_name()

    return JSStatements([
        JSForStatement(
            JSVarStatement(
                [name.id, __i, __list,__bound],
                [None, JSNum(0), expr,
                 JSAttribute(JSName(__list), 'length')]
            ),
            JSBinOp(
                JSName(__i),
                JSOpLt(),
                JSName(__bound)),
            JSExpressionStatement(
                JSAugAssignStatement(
                    JSName(__i),
                    JSOpAdd(),
                    JSNum(1))),
            [
                JSExpressionStatement(
                    JSAssignmentExpression(
                        JSName(name.id),
                        JSSubscript(
                            JSName(__list),
                            JSName(__i))))
            ] + body)])


For = [For_range, For_dict, For_default]
