# -*- coding: utf-8 -*-
# :Project:  pj -- exceptions transformations
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast

from ..js_ast import (
    JSBinOp,
    JSIfStatement,
    JSName,
    JSNewCall,
    JSOpInstanceof,
    JSStatements,
    JSThrowStatement,
    JSTryCatchFinallyStatement,
)


def Try(t, x):
    t.unsupported(x, x.orelse, "'else' block of 'try' statement isn't supported")
    ename = None
    if x.handlers:
        for h in x.handlers:
            t.unsupported(x,  not (h.type is None or isinstance(h.type, ast.Name)),
                          "'except' expressions must be type names")
            t.unsupported(x, h.name and ename and h.name != ename,
                          "Different per 'except' block exception names aren't"
                          " supported")
            ename = h.name
        ename = ename or 'e'

        if t.has_child(x.handlers, ast.Raise) and t.has_child(x.finalbody, ast.Return):
            t.warn(x, node, "The re-raise in 'except' body may be masked by the "
                   "return in 'final' body.")
            # see
            # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Control_flow_and_error_handling#The_finally_block

        rhandlers = x.handlers.copy()
        rhandlers.reverse()
        prev_except = stmt =  None
        for ix, h in enumerate(rhandlers):
            # if it's  the last except and it's a catchall
            # threat 'except Exception:' as a catchall
            if (ix == 0 and h.type is None or (isinstance(h.type, ast.Name) and
                                   h.type.id == 'Exception')):
                prev_except = JSStatements(h.body)
                continue
            else:
                if ix == 0:
                    prev_except = JSThrowStatement(JSName(ename))
                # then h.type is an ast.Name != 'Exception'
                stmt = JSIfStatement(
                    JSBinOp(JSName(ename), JSOpInstanceof(), JSName(h.type.id)),
                    h.body,
                    prev_except
                )
            prev_except = stmt
        t.ctx['ename'] = ename
        return JSTryCatchFinallyStatement(x.body, ename, prev_except, x.finalbody)


def Raise(t, x):

    if x.exc is None:
        ename = t.ctx.get('ename')
        t.unsupported(x, not ename, "'raise' has no argument but failed obtaining"
                      " implicit exception")
        res = JSThrowStatement(JSName(ename))
    elif isinstance(x.exc, ast.Call) and isinstance(x.exc.func, ast.Name) and \
         len(x.exc.args) == 1 and x.exc.func.id == 'Exception':
        res = JSThrowStatement(JSNewCall(JSName('Error'), x.exc.args))
    else:
        res = JSThrowStatement(x.exc)

    return res
