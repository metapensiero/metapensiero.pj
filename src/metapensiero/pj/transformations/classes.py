# -*- coding: utf-8 -*-
# :Project:  pj -- class transformations
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast

from ..processor.util import controlled_ast_walk

from ..js_ast import (
    JSAssignmentExpression,
    JSAttribute,
    JSCall,
    JSClass,
    JSDict,
    JSExpressionStatement,
    JSList,
    JSName,
    JSStatements,
    JSStr,
    JSSuper,
)


EXC_TEMPLATE = """\
class %(name)s(Error):

    def __init__(self, message):
        self.name = '%(name)s'
        self.message = message or 'Error'
"""

EXC_TEMPLATE_ES5 = """\
def %(name)s(message):
    self.name = '%(name)s'
    self.message = message or 'Custom error %(name)s'
    if typeof(Error.captureStackTrace) == 'function':
        Error.captureStackTrace(self, self.constructor)
    else:
        self.stack = Error(message).stack

%(name)s.prototype = Object.create(Error.prototype);
%(name)s.prototype.constructor = %(name)s;
"""


def _isdoc(el):
    return isinstance(el, ast.Expr) and isinstance(el.value, ast.Str)


def _class_guards(t, x):
    t.es6_guard(x, "'class' statement requires ES6")
    t.unsupported(x, len(x.bases) > 1, "Multiple inheritance is not supported")
    body = x.body
    for node in body:
        t.unsupported(x, not (isinstance(node, (ast.FunctionDef,
                                                ast.AsyncFunctionDef,
                                                ast.Assign)) or \
                              _isdoc(node) or isinstance(node, ast.Pass)),
                      "Class' body members must be functions or assignements")
        t.unsupported(x, isinstance(node, ast.Assign) and len(node.targets) > 1,
                      "Assignements must have only one target")
    if len(x.bases) > 0:
        assert len(x.bases) == 1
        assert isinstance(x.bases[0], ast.Name)
    assert not x.keywords, x.keywords


def ClassDef_exception(t, x):
    """This converts a class like::

      class MyError(Exception):
          pass

    Into something like::

      class MyError extends Error {
          constructor(message) {
              this.name = 'MyError';
              this.message = message || 'Error';
          }
      }

    The real implementation avoids ES6 classes because as of now
    (2016-03-20) subclassing from Error fails the instanceof test and
    so i would break catch bodies, as for how they are transformed
    right now.

    N.B. A toString() like this is supposed to be implemented by the
    Error object:

    function toString() {
        return this.name + ': ' + this.message;
    }
    """
    # detect if the body is empty
    _class_guards(t, x)
    name = x.name
    body = x.body
    if len(x.bases) > 0:
        super_name = x.bases[0].id
    else:
        super_name = None

    # strip docs from body
    fn_body = [e for e in body if isinstance(e, (ast.FunctionDef,
                                                 ast.AsyncFunctionDef))]

    # all the other kind of members which are assigned stuff
    assigns = [e for e in body if isinstance(e, ast.Assign)]

    # is this a simple definition of a subclass of Exception?
    if len(fn_body) > 0 or len(assigns) > 0 or super_name not in \
       ('Exception', 'Error'):
        return
    res = t.subtransform(EXC_TEMPLATE_ES5 % dict(name=name), remap_to=x)
    return res


def ClassDef_default(t, x):
    """Converts a class to an ES6 class."""

    # check if translatable
    _class_guards(t, x)

    name = x.name
    body = x.body

    if len(x.bases) > 0:
        superclass = JSName(x.bases[0].id)
    else:
        superclass = None

    # strip docs from body
    fn_body = [e for e in body if isinstance(e, (ast.FunctionDef,
                                                 ast.AsyncFunctionDef))]

    # all the other kind of members which are assigned stuff
    assigns = [e for e in body if isinstance(e, ast.Assign)]

    # Each FunctionDef must have self as its first arg
    # silly check for methods
    for node in fn_body:
        arg_names = [arg.arg for arg in node.args.args]
        t.unsupported(node, len(arg_names) == 0 or arg_names[0] != 'self',
                      "First arg on method must be 'self'")

    # TODO: better express this... find if the constructor has to be the first
    # as per ES6 doc
    if len(fn_body) > 0 and fn_body[0].name == '__init__':
        init = body[0]
        # __init__ should not contain a return statement
        # silly check
        for stmt in controlled_ast_walk(init):
            assert not isinstance(stmt, ast.Return)

    # manage decorators. some are managed at class translation time and
    # converted to equal ES6 syntax while the generic ones will be calculated
    # at runtime
    decos = {}
    for fn in fn_body:
        # make sure the function hasn't any decorator managed by the function
        # transformer. This includes property, property, classmethod,
        # staticmethod and property.setter:
        if fn.decorator_list and not \
           ((len(fn.decorator_list) == 1 and
            isinstance(fn.decorator_list[0], ast.Name) and
            fn.decorator_list[0].id in ['property', 'classmethod',
                                        'staticmethod']) or
            (isinstance(fn.decorator_list[0], ast.Attribute) and
             fn.decorator_list[0].attr == 'setter')):

            decos[JSStr(fn.name)] = fn.decorator_list
            fn.decorator_list = []  # remove so that the function transformer
            # will not complain

    # keep class doc if present
    if _isdoc(body[0]):
        fn_body = [body[0]] + fn_body

    # assign incoming pynode to the JSClass for the sourcemap
    cls = JSClass(JSName(name), superclass, fn_body)
    cls.py_node = x

    stmts = [cls]

    # prepare assignments mapping as js ast
    def _from_assign_to_dict_item(e):
        key = e.targets[0]
        value = e.value
        if isinstance(key, ast.Name):
            key = ast.Str(key.id)
        return key, value

    assigns = tuple(zip(*map(_from_assign_to_dict_item, assigns)))

    # render assignments as properties at runtime
    if assigns:
        from ..snippets import set_properties
        t.add_snippet(set_properties)
        assigns = JSExpressionStatement(
            JSCall(
                JSAttribute(JSName('_pj'), 'set_properties'),
                (JSName(name),
                 JSDict(assigns[0], assigns[1])),
            )
        )
        stmts.append(assigns)

    # calculate method decorators at runtime
    if decos:
        from ..snippets import set_decorators
        t.add_snippet(set_decorators)
        keys = []
        values = []
        for k, v in decos.items():
            keys.append(k)
            values.append(JSList(v))
        decos = JSExpressionStatement(
            JSCall(
                JSAttribute(JSName('_pj'), 'set_decorators'),
                (JSName(name),
                 JSDict(keys, values)),
            )
        )
        stmts.append(decos)

    # there is any decorator list on the class
    if x.decorator_list:
        from ..snippets import set_class_decorators
        t.add_snippet(set_class_decorators)
        cls_decos = JSExpressionStatement(
            JSExpressionStatement(
                JSAssignmentExpression(
                    JSName(name),
                    JSCall(
                        JSAttribute(JSName('_pj'), 'set_class_decorators'),
                        (JSName(name),
                         JSList(x.decorator_list)),
                    )
                )
            )
        )
        stmts.append(cls_decos)
    return JSStatements(stmts)


ClassDef = [ClassDef_exception, ClassDef_default]


def Call_super(t, x):
    if isinstance(x.func, ast.Attribute) and isinstance(x.func.value, ast.Call) \
         and isinstance(x.func.value.func, ast.Name) and \
         x.func.value.func.id == 'super':
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
