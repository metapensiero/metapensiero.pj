# -*- coding: utf-8 -*-
# :Project:  pj -- special transformations
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast
from functools import reduce
import re

from ..js_ast import (
    JSAttribute,
    JSBinOp,
    JSCall,
    JSCommentBlock,
    JSDependImport,
    JSDict,
    JSMultipleArgsOp,
    JSName,
    JSNamedImport,
    JSNewCall,
    JSNum,
    JSOpInstanceof,
    JSOpNot,
    JSOpOr,
    JSOpStrongEq,
    JSOpStrongNotEq,
    JSOpTypeof,
    JSPass,
    JSStarImport,
    JSStatements,
    JSThis,
    JSUnaryOp,
)


#### Expr

# docstrings &rarr; comment blocks
def Expr_docstring(t, x):
    if isinstance(x.value, ast.Str):
        return JSCommentBlock(x.value.s)

from .obvious import Expr_default
Expr = [Expr_docstring, Expr_default]


# <code>2**3</code> &rarr; <code>Math.pow(2, 3)</code>
def BinOp_pow(t, x):
    if isinstance(x.op, ast.Pow):
        return JSCall(
            JSAttribute(
                JSName('Math'),
                'pow'),
            [x.left, x.right])


from .obvious import BinOp_default
BinOp = [BinOp_pow, BinOp_default]


# <code>self</code> &rarr; <code>this</code>
def Name_self(t, x):
    if x.id == 'self':
        return JSThis()

from .obvious import Name_default
Name = [Name_self, Name_default]


# <code>typeof(x)</code> &rarr; <code>(typeof x)</code>
def Call_typeof(t, x):
    if (isinstance(x.func, ast.Name) and x.func.id == 'typeof'):
        assert len(x.args) == 1
        return JSUnaryOp(JSOpTypeof(), x.args[0])


def Call_isinstance(t, x):
    """Translates ``isinstance(foo, Bar)`` to ``foo instanceof Bar`` and
    ``isinstance(Foo, (Bar, Zoo))`` to ``foo instanceof Bar || foo instanceof
    Zoo``.

    ast dump of the latter::

      Call(args=[Name(ctx=Load(),
                      id='foo'),
                 Tuple(ctx=Load(),
                       elts=[Name(ctx=Load(),
                                  id='Bar'),
                             Name(ctx=Load(),
                                  id='Zoo')])],
           func=Name(ctx=Load(),
                     id='isinstance'),
           keywords=[])

    """
    if (isinstance(x.func, ast.Name) and x.func.id == 'isinstance'):
        assert len(x.args) == 2
        if isinstance(x.args[1], ast.Name):
            return JSBinOp(x.args[0], JSOpInstanceof(), x.args[1])
        elif isinstance(x.args[1], (ast.Tuple, ast.List, ast.Set)):
            classes = x.args[1].elts
            target = x.args[0]
            args = tuple((target, c) for c in classes)
            return JSMultipleArgsOp(JSOpInstanceof(), JSOpOr(), *args)


# <code>print(...)</code> &rarr; <code>console.log(...)</code>
def Call_print(t, x):
    if (isinstance(x.func, ast.Name) and x.func.id == 'print'):
        return JSCall(JSAttribute(JSName('console'), 'log'), x.args)


# <code>len(x)</code> &rarr; <code>x.length</code>
def Call_len(t, x):
    if (isinstance(x.func, ast.Name) and x.func.id == 'len' and
        len(x.args) == 1):
        return JSAttribute(x.args[0], 'length')


def Call_str(t, x):
    if (isinstance(x.func, ast.Name) and x.func.id == 'str' and
        len(x.args) == 1):
        return JSCall(JSAttribute(JSName(x.args[0]), 'toString'), [])


def Call_new(t, x):
    """Translates ``Foo(...) to ``new Foo(...)`` if function name starts
    with a capital letter.
    """
    def getNameString(x):
        if isinstance(x, ast.Name):
            return x.id
        elif isinstance(x, ast.Attribute):
            return str(x.attr)
        elif isinstance(x, ast.Subscript):
            if isinstance(x.slice, ast.Index):
                return str(x.slice.value)

    NAME_STRING = getNameString(x.func)

    res = None

    if (NAME_STRING and re.search(r'^[A-Z]', NAME_STRING)):
        # TODO: generalize args mangling and apply here
        # assert not any([x.keywords, x.starargs, x.kwargs])
        res = JSNewCall(x.func, x.args)
    elif isinstance(x.func, ast.Name) and x.func.id == 'new':
        res = JSNewCall(x.args[0].func, x.args[0].args)
    return res

def Call_import(t, x):
    if (isinstance(x.func, ast.Name) and x.func.id == '__import__'):
        assert len(x.args) == 1 and isinstance(x.args[0], ast.Str)
        t.es6_guard(x, "'__import__()' call requires ES6")
        return JSDependImport(x.args[0].s)


def Call_type(t, x):
    if (isinstance(x.func, ast.Name) and x.func.id == 'type'):
        assert len(x.args) == 1
        return JSCall(JSAttribute(JSName('Object'), 'getPrototypeOf'), x.args)


def Call_dict_update(t, x):
    """Converts ``dict(foo).update(bar)`` to ``Object.assign(foo, bar)``.

    requires ES6
    ast dump::

      Expr(value=Call(args=[Name(ctx=Load(),
                                 id='bar')],
                      func=Attribute(attr='update',
                                     ctx=Load(),
                                     value=Call(args=[Name(ctx=Load(),
                                                           id='foo')],
                                                func=Name(ctx=Load(),
                                                          id='dict'),
                                                keywords=[])),
                      keywords=[]))

    """
    if isinstance(x.func, ast.Attribute) and x.func.attr == 'update' and \
       isinstance(x.func.value, ast.Call) and  \
       isinstance(x.func.value.func, ast.Name) and \
       x.func.value.func.id == 'dict' and  len(x.func.value.args) == 1:
        t.es6_guard(x, "dict.update() requires ES6")
        return JSCall(
            JSAttribute(JSName('Object'), 'assign'),
            [JSName(x.func.value.args[0].id)] + x.args
            )


def Call_dict_copy(t, x):
    """Converts ``dict(foo).copy()`` to ``Object.assign({}, foo)``.

    requires ES6
    ast dump::

      Expr(value=Call(args=[],
                      func=Attribute(attr='copy',
                                     ctx=Load(),
                                     value=Call(args=[Name(ctx=Load(),
                                                           id='foo')],
                                                func=Name(ctx=Load(),
                                                          id='dict'),
                                                keywords=[])),
                      keywords=[]))
    """
    if isinstance(x.func, ast.Attribute) and x.func.attr == 'copy' and \
       isinstance(x.func.value, ast.Call) and  \
       isinstance(x.func.value.func, ast.Name) and \
       x.func.value.func.id == 'dict' and  len(x.func.value.args) == 1:
        t.es6_guard(x, "dict.copy() requires ES6")
        return JSCall(
            JSAttribute(JSName('Object'), 'assign'),
            (JSDict([], []), JSName(x.func.value.args[0].id))
            )


from .classes import Call_super
from .obvious import Call_default
Call = [Call_typeof, Call_isinstance, Call_print, Call_len,
        Call_new, Call_super, Call_import, Call_str, Call_type,
        Call_dict_update, Call_dict_copy, Call_default]


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


#### Import

INSIDE_DUNDER_RE = re.compile(r'([a-zA-Z0-9])__([a-zA-Z0-9])')
def _replace_inside_dunder(name):
    return INSIDE_DUNDER_RE.sub(r'\1-\2', name)

def Import(t, x):
    t.es6_guard(x, "'import' statement requires ES6")
    names = []
    for n in x.names:
        names.append(n.asname or n.name)
    t.add_globals(*names)
    result = []
    for n in x.names:
        old_name = n.name
        n.name = _replace_inside_dunder(n.name)
        t.unsupported(x, (old_name != n.name) and not n.asname,
        "A module name cannot contain dashes, use 'as' to give it a new name.")
        path_module = '/'.join(n.name.split('.'))
        result.append(
            JSStarImport(path_module, n.asname or n.name)
        )
    return JSStatements(result)

def ImportFrom(t, x):
    names = []
    for n in x.names:
        names.append(n.asname or n.name)
    if x.module == '__globals__':
        assert x.level == 0
        # assume a fake import to import js stuff from root object
        t.add_globals(*names)
        result = JSPass()
    else:
        t.es6_guard(x, "'import from' statement requires ES6")
        t.add_globals(*names)
        result = JSPass()
        if x.module:
            path_module = '/'.join(_replace_inside_dunder(x.module).split('.'))
            if x.level == 1:
                # from .foo import bar
                path_module = './' + path_module
            elif x.level > 1:
                # from ..foo import bar
                # from ...foo import bar
                path_module = '../' * (x.level - 1) + path_module
            result = JSNamedImport(path_module,
                                   [(n.name, n.asname) for n in x.names])
        else:
            assert x.level > 0
            result = []
            for n in x.names:
                if x.level == 1:
                    # from . import foo
                    result.append(
                        JSStarImport('./' + n.name, n.asname or n.name)
                    )
                else:
                    # from .. import foo
                    result.append(
                        JSStarImport('../' * x.level + n.name,
                                     n.asname or n.name)
                    )
            result = JSStatements(result)
    return result


from .obvious import Compare_default

def Compare_in(t, x):
    if not isinstance(x.ops[0], (ast.NotIn, ast.In)):
        return
    if t.enable_snippets:
        from ..snippets import _in, in_es6
        if t.enable_es6:
            t.add_snippet(in_es6)
            sname = 'in_es6'
        else:
            t.add_snippet(_in)
            sname = '_in'
        result = JSCall(JSAttribute('_pj', sname), [x.left, x.comparators[0]])
        if isinstance(x.ops[0], ast.NotIn):
            result = JSUnaryOp(JSOpNot(), result)
        return result

Compare = [Compare_in, Compare_default]

def Subscript_slice(t, x):

    if isinstance(x.slice, ast.Slice):
        slice = x.slice
        t.unsupported(x, slice.step and slice.step != 1, "Slice step is unsupported")
        args = []
        if slice.lower:
            args.append(slice.lower)
        else:
            args.append(JSNum(0))
        if slice.upper:
            args.append(slice.upper)

        return JSCall(JSAttribute(x.value, 'slice'), args)

from .obvious import Subscript_default

Subscript = [Subscript_slice, Subscript_default]

from .obvious import Attribute_default

def Attribute_list_append(t, x):
    """Converts ``list(foo).append(bar)`` to ``foo.push(bar)``.

    ast dump::

      Expr(value=Call(args=[Name(ctx=Load(),
                                 id='bar')],
                      func=Attribute(attr='append',
                                     ctx=Load(),
                                     value=Call(args=[Name(ctx=Load(),
                                                           id='foo')],
                                                func=Name(ctx=Load(),
                                                          id='list'),
                                                keywords=[])),
                      keywords=[]))
    """
    if x.attr == 'append' and isinstance(x.value, ast.Call) and \
       isinstance(x.value.func, ast.Name) and x.value.func.id == 'list' and \
       len(x.value.args) == 1:
        return JSAttribute(JSName(x.value.args[0].id), 'push')


Attribute = [Attribute_list_append, Attribute_default]
