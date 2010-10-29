
#### Statements

import ast
from functools import reduce
from pj.js_ast import *

# Assign
def Assign(t, x):
    y = JSAssignmentExpression(x.targets[-1], x.value)
    for i in range(len(x.targets) - 1):
        y = JSAssignmentExpression(x.targets[-(2 + i)], y)
    return JSExpressionStatement(y)

# **AugAssign**
def AugAssign(t, x):
    return JSAugAssignStatement(x.target, x.op, x.value)

# **If**
def If(t, x):
    return JSIfStatement(x.test, x.body, x.orelse)

# **While**
def While(t, x):
    assert not x.orelse
    return JSWhileStatement(x.test, x.body)

# **Break**
def Break(t, x):
    return JSBreakStatement()

# **Continue**
def Continue(t, x):
    return JSContinueStatement()

# **Pass**
def Pass(t, x):
    return JSPass()

# **Return** 
# 
# x.value is None for blank return statements
def Return(t, x):
    return JSReturnStatement(x.value)

# **Delete**
def Delete(t, x):
    for t in x.targets:
        assert isinstance(t, ast.Subscript)
        assert isinstance(t.slice, ast.Index)
    return JSStatements([
                JSDeleteStatement(t.value, t.slice.value)
                for t in x.targets])


#### Expressions

# **Expr**
#
# See [pj.transformations.special](special.py) for special cases
def Expr_default(t, x):
    return JSExpressionStatement(x.value)

# **List**
def List(t, x):
    return JSList(x.elts)

# **Tuple**
def Tuple(t, x):
    return JSList(x.elts)

# **Tuple**
def Dict(t, x):
    return JSDict(x.keys, x.values)

# **Lambda**
def Lambda(t, x):
    assert not any(getattr(x.args, k) for k in [
            'vararg', 'varargannotation', 'kwonlyargs', 'kwarg',
            'kwargannotation', 'defaults', 'kw_defaults'])
    return JSFunction(
                None,
                [arg.arg for arg in x.args.args],
                [JSReturnStatement(x.body)])

# **IfExp**
def IfExp(t, x):
    return JSIfExp(x.test, x.body, x.orelse)

# **Call**
#
# See [pj.transformations.special](special.py) for special cases
def Call_default(t, x):
    assert not any([x.keywords, x.starargs, x.kwargs])
    return JSCall(x.func, x.args)

# **Attribute**
def Attribute(t, x):
    return JSAttribute(x.value, str(x.attr))

# **Subscript**
def Subscript(t, x):
    if isinstance(x.slice, ast.Index):
        return JSSubscript(x.value, x.slice.value)

# **UnaryOp**
def UnaryOp(t, x):
    return JSUnaryOp(x.op, x.operand)

# **BinOp**
#
# See [pj.transformations.special](special.py) for special cases
def BinOp_default(t, x):
    return JSBinOp(x.left, x.op, x.right)

# **BoolOp**
def BoolOp(t, x):
    return reduce(
                lambda left, right: JSBinOp(left, x.op, right),
                x.values)

# **Compare**
def Compare(t, x):
    exps = [x.left] + x.comparators
    bools = []
    for i in range(len(x.ops)):
        bools.append(JSBinOp(exps[i], x.ops[i], exps[i + 1]))
    return reduce(
            lambda x, y: JSBinOp(x, JSOpAnd(), y),
            bools)

#### Atoms

# **Num**
def Num(t, x):
    return JSNum(x.n)

# **Str**
def Str(t, x):
    return JSStr(x.s)

# **Name**
# 
# {True,False,None} are Names
def Name_default(t, x):
    cls = {
        'True': JSTrue,
        'False': JSFalse,
        'None': JSNull,
    }.get(x.id)
    if cls:
        return cls()
    else:
        return JSName(x.id)

#### Ops

# <code>in</code>
def In(t, x):
  return JSOpIn()

# <code>+</code>
def Add(t, x):
    return JSOpAdd()

# <code>-</code>
def Sub(t, x):
    return JSOpSub()

# <code>*</code>
def Mult(t, x):
    return JSOpMult()

# <code>/</code>
def Div(t, x):
    return JSOpDiv()

# <code>%</code>
def Mod(t, x):
    return JSOpMod()

# <code>and</code>
def And(t, x):
    return JSOpAnd()

# <code>or</code>
def Or(t, x):
    return JSOpOr()

# <code>not</code>
def Not(t, x):
    return JSOpNot()

# <code>==</code> and <code>!=</code> are in [special.py](special.py)
# because they transform to <code>===</code> and <code>!==</code>

# <code>&lt;</code>
def Lt(t, x):
    return JSOpLt()

# <code>&lt;=</code>
def LtE(t, x):
    return JSOpLtE()

# <code>&gt;</code>
def Gt(t, x):
    return JSOpGt()

# <code>&gt;=</code>
def GtE(t, x):
    return JSOpGtE()


