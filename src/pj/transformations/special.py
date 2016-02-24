import ast, re
from pj.js_ast import *


#### Expr

# docstrings &rarr; comment blocks
def Expr_docstring(t, x):
    if isinstance(x.value, ast.Str):
        return JSCommentBlock(x.value.s)

from pj.transformations.obvious import Expr_default
Expr = [Expr_docstring, Expr_default]


#### BinOp
# <code>2**3</code> &rarr; <code>Math.pow(2, 3)</code>
def BinOp_pow(t, x):
    if isinstance(x.op, ast.Pow):
        return JSCall(
            JSAttribute(
                JSName('Math'),
                'pow'),
            [x.left, x.right])


from pj.transformations.obvious import BinOp_default
BinOp = [BinOp_pow, BinOp_default]


#### Name
# <code>self</code> &rarr; <code>this</code>
def Name_self(t, x):
    if x.id == 'self':
        return JSThis()

from pj.transformations.obvious import Name_default
Name = [Name_self, Name_default]

#### Call

# <code>typeof(x)</code> &rarr; <code>(typeof x)</code>
def Call_typeof(t, x):
    if (
            isinstance(x.func, ast.Name) and
            x.func.id == 'typeof'):
        assert len(x.args) == 1
        return JSUnaryOp(
                    JSOpTypeof(),
                    x.args[0])


# <code>isinstance(x, y)</code> &rarr; <code>(x instanceof y)</code>
def Call_isinstance(t, x):
    if (
            isinstance(x.func, ast.Name) and
            x.func.id == 'isinstance'):
        assert len(x.args) == 2
        return JSBinOp(
                    x.args[0],
                    JSOpInstanceof(),
                    x.args[1])



# <code>print(...)</code> &rarr; <code>console.log(...)</code>
def Call_print(t, x):
    if (
            isinstance(x.func, ast.Name) and
            x.func.id == 'print'):
        return JSCall(
                    JSAttribute(
                        JSName('console'),
                        'log'),
                    x.args)


# <code>len(x)</code> &rarr; <code>x.length</code>
def Call_len(t, x):
    if (
            isinstance(x.func, ast.Name) and
            x.func.id == 'len' and
            len(x.args) == 1):
        return JSAttribute(
                        x.args[0],
                        'length')


#### Call_new
#
# Transform
#<pre>Foo(...)</pre>
# to
#<pre>(new Foo(...))</pre>
# More generally, this transformation applies iff a Name starting with <code>[A-Z]</code> is Called.
def Call_new(t, x):

    def getNameString(x):
        if isinstance(x, ast.Name):
            return x.id
        elif isinstance(x, ast.Attribute):
            return str(x.attr)
        elif isinstance(x, ast.Subscript):
            if isinstance(x.slice, ast.Index):
                return str(x.slice.value)

    NAME_STRING = getNameString(x.func)

    if NAME_STRING and re.search(r'^[A-Z]', NAME_STRING):
        #assert not any([x.keywords, x.starargs, x.kwargs])
        return JSNewCall(x.func, x.args)


from pj.transformations.classes import Call_super
from pj.transformations.obvious import Call_default
Call = [Call_typeof, Call_isinstance, Call_print, Call_len, Call_new, Call_super, Call_default]


#### Ops

# <code>==</code>
#
# Transform to <code>===</code>
def Eq(t, x):
    return JSOpStrongEq()

Is = Eq

# <code>!=</code>
#
# Transform to <code>!==</code>
def NotEq(t, x):
    return JSOpStrongNotEq()


#### ImportFrom
# Only accept imports of these forms:
# <code>from foo import ...names...</code>
# <code>from foo import *</code>
def ImportFrom(t, x):
    for name in x.names:
        assert name.asname is None
    assert x.level == 0
    return JSPass()
