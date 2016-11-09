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
    JSAttribute,
    JSCall,
    JSClass,
    JSName,
    JSSuper,
)


EXC_TEMPLATE="""\
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
    t.unsupported(x, x.decorator_list, "Class decorators are unsupported")
    t.unsupported(x, len(x.bases) > 1, "Multiple inheritance is not supported")
    body = x.body
    for node in body:
        t.unsupported(x, not (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                              or _isdoc(node) or isinstance(node, ast.Pass)) ,
                      "Class' body members must be functions")

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
    body = [e for e in body if isinstance(e, (ast.FunctionDef, ast.AsyncFunctionDef))]

    # is this a simple definition of a subclass of Exception?
    if len(body) > 0 or super_name not in ('Exception', 'Error'):
        return
    res = t.subtransform(EXC_TEMPLATE_ES5 % dict(name=name), remap_to=x)
    return res



def ClassDef_default(t, x):
    """Converts a class to an ES6 class."""
    _class_guards(t, x)
    name = x.name
    body = x.body
    if len(x.bases) > 0:
        super_name = x.bases[0].id
    else:
        super_name = None

    # strip docs from body
    body = [e for e in body if isinstance(e, (ast.FunctionDef, ast.AsyncFunctionDef))]

    # * Each FunctionDef must have self as its first arg
    # silly check for methods
    for node in body:
        arg_names = [arg.arg for arg in node.args.args]
        t.unsupported(node, len(arg_names) == 0 or arg_names[0] != 'self',
                      "First arg on method must be 'self'")

    if len(body) > 0 and body[0].name == '__init__':
        init = body[0]
        # * __init__ may not contain a return statement
        # silly check
        init_args = [arg.arg for arg in init.args.args]
        init_body = init.body
        for stmt in controlled_ast_walk(init):
            assert not isinstance(stmt, ast.Return)

    if super_name:
        superclass = JSName(super_name)
    else:
        superclass = None

    return JSClass(JSName(name), superclass, body)


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
