# -*- coding: utf-8 -*-
# :Project:  pj -- class and function transformations
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast

from ..processor.util import body_local_names

from ..js_ast import *


def ClassDef(t, x):

    t.es6_guard(x, "'class' statement requires ES6")
    assert not x.keywords, x.keywords
    #assert not x.starargs, x.starargs
    #assert not x.kwargs, x.kwargs
    assert not x.decorator_list, x.decorator_list

    name = x.name
    body = x.body
    if len(x.bases) > 0:
        assert len(x.bases) == 1
        assert isinstance(x.bases[0], ast.Name)
        super_name = x.bases[0].id
    else:
        super_name = None

    # Enforced restrictions:

    # * The class body must consist of nothing but FunctionDefs
    for node in body:
        assert isinstance(node, ast.FunctionDef)

    # * Each FunctionDef must have self as its first arg
    for node in body:
        arg_names = [arg.arg for arg in node.args.args]
        assert len(arg_names) > 0 and arg_names[0] == 'self'

    # * (You need __init__) and (it must be the first FunctionDef)
    assert len(body) > 0
    init = body[0]
    assert str(init.name) == '__init__'

    # * __init__ may not contain a return statement
    init_args = [arg.arg for arg in init.args.args]
    init_body = init.body
    for stmt in ast.walk(init):
        assert not isinstance(stmt, ast.Return)

    if super_name:
        superclass = JSName(super_name)
    else:
        superclass = None

    return JSClass(JSName(name), superclass, body)


def Call_super(t, x):
    if isinstance(x.func, ast.Attribute) and isinstance(x.func.value, ast.Call) \
         and isinstance(x.func.value.func, ast.Name) and x.func.value.func.id == 'super':
        sup_args = x.func.value.args
        # Are we in a FuncDef and is it a method and super() has no args?
        method = t.find_parent(x, ast.FunctionDef)
        if method and isinstance(t.parent_of(method), ast.ClassDef) and \
           len(sup_args) == 0:
            # if in class constructor, this becomes ``super(x, y)``
            if method.name == '__init__':
                result = JSCall(JSSuper(), x.args)
            else:
                sup_method = x.func.attr
                # this becomes super.method(x, y)
                result = JSCall(
                    JSAttribute(JSSuper(), sup_method),
                    x.args
                )
            return result


def FunctionDef(t, x):

    assert not x.decorator_list
    assert not any(getattr(x.args, k, False) for k in [
            'vararg', 'varargannotation', 'kwonlyargs', 'kwarg',
            'kwargannotation', 'defaults', 'kw_defaults'])

    NAME = x.name
    ARGS = [arg.arg for arg in x.args.args]
    body = x.body

    # <code>var ...local vars...</code>
    local_vars = list(set(body_local_names(body)) - set(ARGS))
    if len(local_vars) > 0:
        body = [JSVarStatement(
                            local_vars,
                            [None] * len(local_vars))] + body

    # If x is a method
    if isinstance(t.parent_of(x), ast.ClassDef):

        # Skip ``self``
        ARGS = ARGS[1:]

        if NAME == '__init__':
            result = JSClassConstructor(ARGS, body)
        else:
            result = JSMethod(str(NAME), ARGS, body)
    # x is a function
    else:
        result = JSFunction(
            str(NAME),
            ARGS,
            body
        )
    return result
