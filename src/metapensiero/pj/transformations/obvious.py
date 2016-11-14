# -*- coding: utf-8 -*-
# :Project:  pj -- simpler transformations
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast
from functools import reduce

from ..js_ast import (
    JSAssignmentExpression,
    JSAttribute,
    JSAugAssignStatement,
    JSAwait,
    JSBinOp,
    JSBreakStatement,
    JSCall,
    JSContinueStatement,
    JSDeleteStatement,
    JSDict,
    JSExport,
    JSExpressionStatement,
    JSFalse,
    JSFunction,
    JSIfExp,
    JSIfStatement,
    JSList,
    JSName,
    JSNull,
    JSNum,
    JSOpAdd,
    JSOpAnd,
    JSOpBitAnd,
    JSOpBitOr,
    JSOpBitXor,
    JSOpDiv,
    JSOpGt,
    JSOpGtE,
    JSOpIn,
    JSOpInvert,
    JSOpLShift,
    JSOpLt,
    JSOpLtE,
    JSOpMod,
    JSOpMult,
    JSOpNot,
    JSOpOr,
    JSOpRShift,
    JSOpSub,
    JSOpUSub,
    JSPass,
    JSRest,
    JSReturnStatement,
    JSStatements,
    JSStr,
    JSSubscript,
    JSTrue,
    JSUnaryOp,
    JSWhileStatement,
    JSYield,
    JSYieldStar,
)


#### Statements


def Assign_default(t, x):
    y = JSAssignmentExpression(x.targets[-1], x.value)
    for i in range(len(x.targets) - 1):
        y = JSAssignmentExpression(x.targets[-(2 + i)], y)
    return JSExpressionStatement(y)


def Assign_all(t, x):
    if len(x.targets) == 1 and isinstance(x.targets[0], ast.Name) and \
       x.targets[0].id == '__all__':
        t.es6_guard(x, "'__all__' assignement requires ES6")
        elements = x.value.elts
        result = [JSExport(el.s) for el in elements]
        return JSStatements(result)

Assign = [Assign_all, Assign_default]


def AugAssign(t, x):
    return JSAugAssignStatement(x.target, x.op, x.value)


def If(t, x):
    return JSIfStatement(x.test, x.body, x.orelse)


def While(t, x):
    assert not x.orelse
    return JSWhileStatement(x.test, x.body)


def Break(t, x):
    return JSBreakStatement()


def Continue(t, x):
    return JSContinueStatement()


def Pass(t, x):
    return JSPass()


def Return(t, x):
    # x.value is None for blank return statements
    return JSReturnStatement(x.value)


def Delete(t, x):
    for t in x.targets:
        assert isinstance(t, ast.Subscript)
        assert isinstance(t.slice, ast.Index)
    return JSStatements([
                JSDeleteStatement(t.value, t.slice.value)
                for t in x.targets])


def Await(t, x):
    t.stage3_guard(x, "Async stuff requires 'stage3' to be enabled")
    return JSAwait(x.value)


#### Expressions


def Expr_default(t, x):
    # See [pj.transformations.special](special.py) for special cases
    return JSExpressionStatement(x.value)


def List(t, x):
    return JSList(x.elts)


def Tuple(t, x):
    return JSList(x.elts)


def Dict(t, x):
    return JSDict(x.keys, x.values)


def Lambda(t, x):
    assert not any(getattr(x.args, k) for k in [
            'vararg', 'kwonlyargs', 'kwarg', 'defaults', 'kw_defaults'])
    return JSFunction(
                None,
                [arg.arg for arg in x.args.args],
                [JSReturnStatement(x.body)])


def IfExp(t, x):
    return JSIfExp(x.test, x.body, x.orelse)


def Call_default(t, x):
    # See [pj.transformations.special](special.py) for special cases
    kwargs = []
    if x.keywords:
        for kw in x.keywords:
            t.unsupported(x, kw.arg is None, "'**kwargs' syntax ins'nt "
                          "supported")
            kwargs.append((kw.arg, kw.value))
        kwargs = JSDict(*zip(*kwargs))
    else:
        kwargs = None
    return JSCall(x.func, x.args, kwargs)


def Attribute_default(t, x):
    return JSAttribute(x.value, str(x.attr))


def Subscript_default(t, x):
    if isinstance(x.slice, ast.Index):
        return JSSubscript(x.value, x.slice.value)


def UnaryOp(t, x):
    return JSUnaryOp(x.op, x.operand)


def BinOp_default(t, x):
    # See [pj.transformations.special](special.py) for special cases
    return JSBinOp(x.left, x.op, x.right)


def BoolOp(t, x):
    return reduce(
                lambda left, right: JSBinOp(left, x.op, right),
                x.values)


def Compare_default(t, x):
    """Compare is for those expressions like 'x in []' or 1 < x < 10. It's
    different from a binary operations because it can have multiple
    operators and more than two operands."""
    exps = [x.left] + x.comparators
    bools = []
    for i in range(len(x.ops)):
        bools.append(JSBinOp(exps[i], x.ops[i], exps[i + 1]))
    return reduce(lambda x, y: JSBinOp(x, JSOpAnd(), y), bools)


#### Atoms


def Num(t, x):
    return JSNum(x.n)


def Str(t, x):
    return JSStr(x.s)


def Name_default(t, x):
    # {True,False,None} are Names
    cls = {
        'True': JSTrue,
        'False': JSFalse,
        'None': JSNull,
    }.get(x.id)
    if cls:
        return cls()
    else:
        return JSName(x.id)


def NameConstant(t, x):
    cls = {
        True: JSTrue,
        False: JSFalse,
        None: JSNull,
    }[x.value]
    return cls()


def Yield(t, x):
    return JSYield(x.value)


def YieldFrom(t, x):
    return JSYieldStar(x.value)


#### Ops


def In(t, x):
    return JSOpIn()


def Add(t, x):
    return JSOpAdd()


def Sub(t, x):
    return JSOpSub()


def USub(t, x):
    "Handles tokens like '-1'"
    return JSOpUSub()


def Mult(t, x):
    return JSOpMult()


def Div(t, x):
    return JSOpDiv()


def Mod(t, x):
    return JSOpMod()


def RShift(t, x):
    return JSOpRShift()


def LShift(t, x):
    return JSOpLShift()


def BitXor(t, x):
    return JSOpBitXor()


def BitAnd(t, x):
    return JSOpBitAnd()


def BitOr(t, x):
    return JSOpBitOr()


def Invert(t, x):
    return JSOpInvert()


def And(t, x):
    return JSOpAnd()


def Or(t, x):
    return JSOpOr()


def Not(t, x):
    return JSOpNot()


# == and != are in special.py
# because they transform to === and !==


def Lt(t, x):
    return JSOpLt()


def LtE(t, x):
    return JSOpLtE()


def Gt(t, x):
    return JSOpGt()


def GtE(t, x):
    return JSOpGtE()


def Starred(t, x):
    return JSRest(x.value)
