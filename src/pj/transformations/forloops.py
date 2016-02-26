# -*- coding: utf-8 -*-
# :Project:  pj -- for loops transformations
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast

from ..js_ast import *


#### Case: Ranges
# Transform
#<pre>for NAME in rage(BOUND):
#for NAME in rage(START, BOUND):</pre>
# to
#<pre>for (var NAME = 0, __bound = BOUND; NAME < __bound; NAME++)
#for (var NAME = START, __bound = BOUND; NAME < __bound; NAME++)</pre>
def For_range(t, x):
    if (
                isinstance(x.target, ast.Name) and
                isinstance(x.iter, ast.Call) and
                isinstance(x.iter.func, ast.Name) and
                x.iter.func.id == 'range' and
                len(x.iter.args) in [1, 2]) and (not x.orelse):

        NAME = x.target
        LDOTS = x.body
        if len(x.iter.args) == 1:
            START = JSNum(0)
            BOUND = x.iter.args[0]
        else:
            START = x.iter.args[0]
            BOUND = x.iter.args[1]

        __bound = t.new_name()

        return JSForStatement(
                    JSLetStatement(
                        [NAME.id, __bound],
                        [START, BOUND]),
                    JSBinOp(JSName(NAME.id), JSOpLt(), JSName(__bound)),
                    JSAugAssignStatement(
                        JSName(NAME.id), JSOpAdd(), JSNum(1)),
                    LDOTS)

#### Case: Dicts
# Transform
#<pre>for NAME in dict(EXPR):
#    ...</pre>
# to
#<pre>var __dict = EXPR;
#for (var NAME in __dict) {
#    if (__dict.hasOwnProperty(NAME)) {
#       ...
#    }
#}</pre>
def For_dict(t, x):
    if (
            isinstance(x.iter, ast.Call) and
            isinstance(x.iter.func, ast.Name) and
            x.iter.func.id == 'dict' and
            len(x.iter.args) == 1) and (not x.orelse):

        assert isinstance(x.target, ast.Name)

        NAME = x.target
        EXPR = x.iter.args[0]
        LDOTS = x.body

        __dict = t.new_name()

        return JSStatements([
                    JSVarStatement(
                        [__dict],
                        [EXPR]),
                    JSForeachStatement(
                        NAME.id,
                        JSName(__dict),
                        [JSIfStatement(
                            JSCall(
                                JSAttribute(
                                    JSName(__dict),
                                    'hasOwnProperty'),
                                [JSName(NAME.id)]),
                            LDOTS,
                            None)])])


#### Default: assume it's an array
# Transform
#<pre>for NAME in EXPR:
#    ...</pre>
# to
#<pre>var NAME, __list = EXPR;
#for (
#        var __i = 0, __bound = __list.length;
#        __i < __bound;
#        __i++) {
#    NAME = __list[__i];
#    ...
#}</pre>
def For_default(t, x):

    assert isinstance(x.target, ast.Name)

    NAME = x.target
    EXPR = x.iter
    LDOTS = x.body

    __list = t.new_name()
    __bound = t.new_name()
    __i = t.new_name()

    return JSStatements([
                JSVarStatement(
                    [NAME.id, __list],
                    [None, EXPR]),
                JSForStatement(
                    JSVarStatement(
                        [__i, __bound],
                        [
                            JSNum(0),
                            JSAttribute(
                                JSName(__list),
                                'length')]),
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
                                JSName(NAME.id),
                                JSSubscript(
                                    JSName(__list),
                                    JSName(__i))))
                    ] + LDOTS)])


For = [For_range, For_dict, For_default]
