#### Statements

import ast
from functools import reduce
from pj.js_ast import *


def Assign(t, x):
    y = JSAssignmentExpression(x.targets[-1], x.value)
    for i in range(len(x.targets) - 1):
        y = JSAssignmentExpression(x.targets[-(2 + i)], y)
    return JSExpressionStatement(y)


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
            'vararg', 'varargannotation', 'kwonlyargs', 'kwarg',
            'kwargannotation', 'defaults', 'kw_defaults'])
    return JSFunction(
                None,
                [arg.arg for arg in x.args.args],
                [JSReturnStatement(x.body)])


def IfExp(t, x):
    return JSIfExp(x.test, x.body, x.orelse)


def Call_default(t, x):
    # See [pj.transformations.special](special.py) for special cases
    #assert not any([x.keywords, x.starargs, x.kwargs])
    return JSCall(x.func, x.args)


def Attribute(t, x):
    return JSAttribute(x.value, str(x.attr))


def Subscript(t, x):
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


def Compare(t, x):
    exps = [x.left] + x.comparators
    bools = []
    for i in range(len(x.ops)):
        bools.append(JSBinOp(exps[i], x.ops[i], exps[i + 1]))
    return reduce(
            lambda x, y: JSBinOp(x, JSOpAnd(), y),
            bools)

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

# <code>==</code> and <code>!=</code> are in [special.py](special.py)
# because they transform to <code>===</code> and <code>!==</code>

def Lt(t, x):
    return JSOpLt()

def LtE(t, x):
    return JSOpLtE()

def Gt(t, x):
    return JSOpGt()

def GtE(t, x):
    return JSOpGtE()
