# -*- coding: utf-8 -*-
# :Project:  pj -- for loops transformations
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast

from ..js_ast import (
    JSAssignmentExpression,
    JSAttribute,
    JSAugAssignStatement,
    JSBinOp,
    JSCall,
    JSExpressionStatement,
    JSForStatement,
    JSForeachStatement,
    JSForofStatement,
    JSIfStatement,
    JSName,
    JSNum,
    JSOpAdd,
    JSOpLt,
    JSStatements,
    JSSubscript,
    JSVarStatement,
)


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
        1 <= len(x.iter.args) < 4) and (not x.orelse):

        name = x.target
        body = x.body
        if len(x.iter.args) == 1:
            start = JSNum(0)
            bound = x.iter.args[0]
            step = JSNum(1)
        elif len(x.iter.args) == 2:
            start = x.iter.args[0]
            bound = x.iter.args[1]
            step = JSNum(1)
        else:
            start = x.iter.args[0]
            bound = x.iter.args[1]
            step = x.iter.args[2]

        # TODO: as of now this doesn't support range(10, 0, -2)

        __bound = t.new_name()

        return JSForStatement(
            JSVarStatement(
                [name.id, __bound],
                [start, bound]),
            JSBinOp(JSName(name.id), JSOpLt(), JSName(__bound)),
            JSAugAssignStatement(
                JSName(name.id), JSOpAdd(), step),
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
        len(x.iter.args) <= 2) and (not x.orelse):

        t.unsupported(x, not isinstance(x.target, ast.Name),
                      "Target must be a name")

        name = x.target
        expr = x.iter.args[0]
        body = x.body

        __dict = t.new_name()

        # if not ``dict(foo, True)`` filter out inherited values
        if not (len(x.iter.args) == 2 and
            isinstance(x.iter.args[1], ast.NameConstant) and
            x.iter.args[1].value):
            body = [
                    JSIfStatement(
                        JSCall(
                            JSAttribute(JSName(__dict), 'hasOwnProperty'),
                            [JSName(name.id)]
                        ),
                        body, None
                    )
                ]
        # set the incoming py_node for the sourcemap
        loop = JSForeachStatement(
            name.id,
            JSName(__dict),
            body
        )
        loop.py_node = x

        return JSStatements([
            JSVarStatement([__dict], [expr]),
            loop
        ])


def For_iterable(t, x):
    """Special 'for name in iterable(expr)' statement translation. It detects
    the ``iterable()`` call and converts it to:

    .. code:: javascript

      var __iterable = expr;
      for (var name of __iterable) {
          ...
      }
    """
    if (isinstance(x.iter, ast.Call) and
        isinstance(x.iter.func, ast.Name) and
        x.iter.func.id == 'iterable' and
        len(x.iter.args) == 1) and (not x.orelse):

        t.unsupported(x, not isinstance(x.target, ast.Name),
                      "Target must be a name")

        name = x.target
        expr = x.iter.args[0]
        body = x.body

        __iterable = t.new_name()

        # set the incoming py_node for the sourcemap
        loop = JSForofStatement(
            name.id,
            JSName(__iterable),
            body,
        )
        loop.py_node = x
        return JSStatements([
            JSVarStatement([__iterable], [expr]),
            loop
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

    return JSForStatement(
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
        ] + body)


For = [For_range, For_dict, For_iterable, For_default]
