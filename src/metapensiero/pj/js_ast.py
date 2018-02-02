# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj -- JS AST
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>,
#            Lele Gaifax <lele@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import itertools
import json
import re

from .processor.transforming import TargetNode
from .processor.util import delimited, delimited_multi_line


JS_KEYWORDS = set([
    'break', 'case', 'catch', 'continue', 'default', 'delete', 'do', 'else',
    'finally', 'for', 'function', 'if', 'in', 'instanceof', 'new', 'return',
    'switch', 'this', 'throw', 'try', 'typeof', 'var', 'void', 'while', 'with',

    'abstract', 'boolean', 'byte', 'char', 'class', 'const',
    'double', 'enum', 'export', 'extends', 'final', 'float', 'goto',
    'implements', 'import', 'int', 'interface', 'long', 'native', 'package',
    'private', 'protected', 'public', 'short', 'static', 'super',
    'synchronized', 'throws', 'transient', 'volatile'])

JS_KEYWORDS_ES6 = JS_KEYWORDS - set(['delete'])


def _check_keywords(target_node, name):
    trans = target_node.transformer
    if trans is not None:
        trans.unsupported(
            target_node.py_node,
            name in JS_KEYWORDS_ES6 if trans.enable_es6 else name in JS_KEYWORDS,
            "Name '%s' is reserved in JavaScript." % name)
    else:
        if name in JS_KEYWORDS:
            raise ValueError("Name %s is reserved in JavaScript." % name)

#### Misc


class JSNode(TargetNode):
    pass


class JSStatement(JSNode):
    pass


class JSLeftSideUnaryOp(JSNode):
    pass


class JSStatements(JSNode):

    def __iadd__(self, other):
        self.transformed_args.extend(other.transformed_args)
        return self

    def emit(self, statements):
        for s in statements:
            yield s

    def squash(self, args):
        for a in args:
            if isinstance(a, JSStatements):
                yield from a.transformed_args
            else:
                yield a

    def reordered_args(self, args):
        """Reorder the args to keep the imports and vars always at the top."""
        args = list(self.squash(args))
        imports = []
        vars_ = []
        others = []
        for a in args:
            if isinstance(a, JSImport):
                imports.append(a)
            elif isinstance(a, JSVarStatement) and \
                 not a.options.get('unmovable', False):
                vars_.append(a)
            else:
                others.append(a)

        others_first = []
        others_after = []
        # if the others start with some comments, put those at the top
        start_trigger = False
        for s in others:
            if isinstance(s, JSCommentBlock) and not start_trigger:
                others_first.append(s)
            else:
                others_after.append(s)
                start_trigger = True

        return itertools.chain(others_first, imports, vars_, others_after)

    def serialize(self):
        for a in self.emit(self.reordered_args(self.transformed_args)):
            yield from self.lines(a.serialize(), delim=True)


class JSPass(JSNode):
    def emit(self):
        return []


class JSCommentBlock(JSNode):
    def emit(self, text):
        assert text.find('*/') == -1
        yield from self.lines(delimited_multi_line(self, text, '/*', '*/', True))


class JSLiteral(JSNode):
    def emit(self, text):
        yield from self.lines(delimited_multi_line(self, text, '', '', False))

#### Statements


class JSExpressionStatement(JSStatement):
    def emit(self, value):
        yield self.part(value)


class JSVarDeclarer(JSStatement):

    def with_kind(self, kind, keys, values):
        for key in keys:
            _check_keywords(self, key)
        assert len(keys) > 0
        assert len(keys) == len(values)

        arr = ['%s ' % kind]
        for i in range(len(keys)):
            if i > 0:
                arr.append(', ')
            arr.append(keys[i])
            if values[i] is not None:
                arr.append(' = ')
                arr.append(values[i])
        yield self.part(*arr)


class JSVarStatement(JSVarDeclarer):
    def emit(self, keys, values, unmovable=False):
        yield from self.with_kind('var', keys, values)


class JSLetStatement(JSVarDeclarer):
    def emit(self, keys, values, unmovable=True):
        yield from self.with_kind('let', keys, values)


class JSAugAssignStatement(JSStatement):
    def emit(self, target, op, value):
        yield self.part(target, ' ', op, '= ', value, name=str(target))


class JSIfStatement(JSStatement):
    def emit(self, test, body, orelse):
        yield self.line(['if (', test, ') {'])
        yield from self.lines(body, indent=True, delim=True)
        if orelse:
            yield self.line(['} else {'])
            yield from self.lines(orelse, indent=True, delim=True)
            yield self.line('}')
        else:
            yield self.line('}')


class JSWhileStatement(JSStatement):
    def emit(self, test, body):
        yield self.line(['while (', test, ') {'])
        yield from self.lines(body, indent=True, delim=True)
        yield self.line('}')


class JSForStatement(JSStatement):
    def emit(self, left, test, right, body):
        yield self.line(['for (', left, '; ', test, '; ', right, ') {'])
        yield from self.lines(body, indent=True, delim=True)
        yield self.line('}')


class JSForIterableStatement(JSStatement):

    operator = ' of '

    def emit(self, target, source, body):
        yield self.line(['for (var ', self.part(target), self.operator,
                         source, ') {'])
        yield from self.lines(body, indent=True, delim=True)
        yield self.line('}')


class JSForeachStatement(JSForIterableStatement):

    operator = ' in '


class JSForofStatement(JSForIterableStatement):
    pass


class JSReturnStatement(JSStatement):
    def emit(self, value):
        if value:
            result = self.line(['return ', value], delim=True)
        else:
            result = self.line('return', delim=True)
        yield result


class JSBreakStatement(JSStatement):
    def emit(self):
        yield self.part('break')


class JSContinueStatement(JSStatement):
    def emit(self):
        yield self.part('continue')


class JSDeleteStatement(JSStatement):
    def emit(self, value):
        yield self.line(['delete ', value], delim=True)


class JSTryCatchFinallyStatement(JSStatement):
    def emit(self, try_body, target, catch_body, finally_body):
        assert catch_body or finally_body
        yield self.line('try {')
        yield from self.lines(try_body, indent=True, delim=True)
        if catch_body:
            yield self.line(['} catch(', target, ') {'])
            yield from self.lines(catch_body, indent=True, delim=True)
        if finally_body:
            yield self.line(['} finally {'])
            yield from self.lines(finally_body, indent=True, delim=True)
        yield self.line('}')


class JSThrowStatement(JSStatement):
    def emit(self, obj):
        yield self.line(['throw ', obj], delim=True)


class JSImport(JSStatement):
    pass


class JSDependImport(JSImport):
    def emit(self, module):
        yield self.line(['System.import(', "'", module, "'", ')'], delim=True)


class JSNamedImport(JSImport):
    def emit(self, module, names):
        js_names = []
        for name, alias in sorted(names):
            if alias:
                js_names.append(self.part(name, ' as ', alias))
            else:
                js_names.append(self.part(name))
        if len(js_names)==1:
            yield self.line(['import ', js_names[0], " from '", module,
                            "'"], delim=True)
        else:
            yield self.line(['import {', *delimited(', ', js_names),
                             "} from '", module, "'"], delim=True)


class JSStarImport(JSImport):
    def emit(self, module, name):
        yield self.line(['import * as ', name, " from '", module, "'"],
                        delim=True)


class JSExport(JSStatement):
    def emit(self, name):
        yield self.line(['export ', '{', name, '}'], delim=True)


class JSExportDefault(JSStatement):
    def emit(self, name):
        yield self.line(['export default ', name], delim=True)


class JSAwait(JSStatement):

    def emit(self, value):
        yield self.part('await ', value)


class JSFunction(JSStatement):

    begin = 'function '
    bet_args_n_body = ''

    def fargs(self, args, acc=None, kwargs=None):
        result = []
        result.append('(')
        js_args = args.copy()
        if kwargs:
            js_args.append(self.part('{', *delimited(', ', kwargs), '}={}'))
        if acc:
            js_args.append(acc)
        delimited(', ', js_args, dest=result)
        result.append(') ')
        return result

    def emit(self, name, args, body, acc=None, kwargs=None):
        line = [self.begin]
        if name is not None:
            line.append(name)
        line += self.fargs(args, acc, kwargs)
        line += self.bet_args_n_body
        line += ['{']
        yield self.line(line, name=str(name))
        yield from self.lines(body, indent=True, delim=True)
        yield self.line('}')


class JSAsyncFunction(JSFunction):

    begin = 'async function '


class JSGenFunction(JSFunction):

    begin = 'function* '


class JSArrowFunction(JSFunction):

    begin = ''
    bet_args_n_body = '=> '

    def emit(self, name, args, body, acc=None, kwargs=None):
        if name:
            # TODO: split this into an assignment + arrow function
            line = [name, ' = ']
        else:
            line = []
        line += self.fargs(args, acc, kwargs)
        line += self.bet_args_n_body
        line += ['{']
        yield self.line(line)
        yield from self.lines(body, indent=True, delim=True)
        if name:
            yield self.line('}', delim=True)
        else:
            yield self.part('}')


class JSClass(JSStatement):

    def emit(self, name, super_, methods):
        line = ['class ', name]
        if super_ is not None:
            line += [' extends ', super_]
        line += [' {']
        yield self.line(line)
        yield from self.lines(methods, indent=True, delim=True)
        yield self.line('}')


class JSClassMember(JSFunction):

    def with_kind(self, kind, args, body, acc=None, kwargs=None, static=False):
        if static:
            line = ['static ', kind]
        else:
            line = [kind]
        line += self.fargs(args, acc, kwargs)
        line += ['{']
        yield self.line(line)
        yield from self.lines(body, indent=True, delim=True)
        yield self.line('}')


class JSClassConstructor(JSClassMember):

    def emit(self, args, body, acc=None, kwargs=None):
        yield from self.with_kind('constructor', args, body, acc, kwargs)


class JSMethod(JSClassMember):

    def emit(self, name, args, body, acc=None, kwargs=None, static=False):
        yield from self.with_kind(name, args, body, acc, kwargs, static)


class JSAsyncMethod(JSClassMember):

    def emit(self, name, args, body, acc=None, kwargs=None, static=False):
        yield from self.with_kind('async ' + name, args, body, acc, kwargs,
                                  static)


class JSGenMethod(JSClassMember):

    def emit(self, name, args, body, acc=None, kwargs=None, static=False):
        yield from self.with_kind('* ' + name, args, body, acc, kwargs,
                                  static)


class JSGetter(JSClassMember):

    def emit(self, name, body, static=False):
        yield from self.with_kind('get ' + name, [], body, static=static)


class JSSetter(JSClassMember):

    def emit(self, name, arg, body, static=False):
        yield from self.with_kind('set ' + name, [arg], body, static=static)


#### Expressions


class JSList(JSNode):
    def emit(self, elts):
        arr = ['[']
        delimited(', ', elts, dest=arr)
        arr.append(']')
        yield self.part(*arr)


class JSDict(JSNode):
    def emit(self, keys, values):
        arr = ['{']
        for i in range(len(keys)):
            if i > 0:
                arr.append(', ')
            arr.append(keys[i])
            arr.append(': ')
            arr.append(values[i])
        arr.append('}')
        yield self.part(*arr)


class JSAssignmentExpression(JSNode):
    def emit(self, left, right):
        yield self.part(left, ' = ', right)


class JSIfExp(JSNode):
    def emit(self, test, body, orelse):
        yield self.part('(', test, ' ? ', body, ' : ', orelse, ')')


class JSCall(JSNode):

    operator = ''

    def emit(self, func, args, kwargs=None, operator=None):
        operator = operator or self.operator
        kwargs = kwargs or []
        arr = [operator, func, '(']
        fargs = args.copy()
        if kwargs:
            fargs.append(kwargs)
        delimited(', ', fargs, dest=arr)
        arr.append(')')
        yield self.part(*arr)


class JSNewCall(JSCall):

    operator = 'new '


class JSAttribute(JSNode):
    def emit(self, obj, s):
        assert re.search(r'^[a-zA-Z$_][a-zA-Z$_0-9]*$', s)
        _check_keywords(self, s)
        yield self.part(obj, '.', s, name=True)


class JSSubscript(JSNode):
    def emit(self, obj, key):
        yield self.part(self.part(obj, name=True), '[',
                        self.part(key, name=True), ']')


class JSKeySubscript(JSNode):
    def emit(self, key):
        yield self.part('[', self.part(key), ']')


class JSBinOp(JSNode):
    def emit(self, left, op, right):
        yield self.part('(', left, ' ', op, ' ', right, ')')


class JSMultipleArgsOp(JSNode):
    def emit(self, binop, conj, *args):
        assert len(args) > 1
        parts = []
        for ix, arg in enumerate(args):
            if isinstance(binop, (tuple, list)):
                op = binop[ix]
            else:
                op = binop
            if ix > 0:
                parts += [' ', conj, ' ']
            parts += ['(', arg[0], ' ', op, ' ', arg[1], ')']
        yield self.part('(', *parts, ')')


class JSUnaryOp(JSNode):
    def emit(self, op, right):
        assert isinstance(op, JSLeftSideUnaryOp)
        yield self.part('(', op, ' ', right, ')')


class JSYield(JSNode):

    def emit(self, expr):
        yield self.part('yield ', expr)


class JSYieldStar(JSNode):

    def emit(self, expr):
        yield self.part('yield* ', expr)


class JSExpression(JSNode):

    def emit(self, expr):
        yield self.part('(', expr, ')')


#### Atoms


class JSNum(JSNode):
    def emit(self, x):
        yield self.part(str(x))


class JSStr(JSNode):
    def emit(self, s):
        yield self.part(json.dumps(s))


class JSName(JSNode):
    def emit(self, name):
        _check_keywords(self, name)
        yield self.part(name, name=True)


class JSSuper(JSNode):
    def emit(self):
        yield self.part('super')


class JSThis(JSNode):
    def emit(self):
        yield self.part('this')


class JSTrue(JSNode):
    def emit(self):
        yield self.part('true')


class JSFalse(JSNode):
    def emit(self):
        yield self.part('false')


class JSNull(JSNode):
    def emit(self):
        yield self.part('null')


class JSRest(JSNode):
    def emit(self, value):
        yield self.part('...', value)


class JSTaggedTemplate(JSNode):

    def emit(self, value, func):
        text = list(delimited_multi_line(self, value, '`'))
        func = list(func.serialize())
        yield self.part(*func, *text)


class JSTemplateLiteral(JSNode):

    def emit(self, value):
        yield from delimited_multi_line(self, value, '`')


#### Ops


class JSOpIn(JSNode):
    def emit(self):
        yield self.part('in')


class JSOpAnd(JSNode):
    def emit(self):
        yield self.part('&&')


class JSOpOr(JSNode):
    def emit(self):
        yield self.part('||')


class JSOpNot(JSLeftSideUnaryOp):
    def emit(self):
        yield self.part('!')


class JSOpInstanceof(JSNode):
    def emit(self):
        yield self.part('instanceof')


class JSOpTypeof(JSLeftSideUnaryOp):
    def emit(self):
        yield self.part('typeof')


class JSOpAdd(JSNode):
    def emit(self):
        yield self.part('+')


class JSOpSub(JSNode):
    def emit(self):
        yield self.part('-')


class JSOpMult(JSNode):
    def emit(self):
        yield self.part('*')


class JSOpDiv(JSNode):
    def emit(self):
        yield self.part('/')


class JSOpMod(JSNode):
    def emit(self):
        yield self.part('%')


class JSOpRShift(JSNode):
    def emit(self):
        yield self.part('>>')


class JSOpLShift(JSNode):
    def emit(self):
        yield self.part('<<')


class JSOpBitXor(JSNode):
    def emit(self):
        yield self.part('^')


class JSOpBitAnd(JSNode):
    def emit(self):
        yield self.part('&')


class JSOpBitOr(JSNode):
    def emit(self):
        yield self.part('|')


class JSOpInvert(JSLeftSideUnaryOp):
    def emit(self):
        yield self.part('~')


class JSOpUSub(JSLeftSideUnaryOp):
    def emit(self):
        yield self.part('-')


class JSOpStrongEq(JSNode):
    def emit(self):
        yield self.part('===')


class JSOpStrongNotEq(JSNode):
    def emit(self):
        yield self.part('!==')


class JSOpLt(JSNode):
    def emit(self):
        yield self.part('<')


class JSOpLtE(JSNode):
    def emit(self):
        yield self.part('<=')


class JSOpGt(JSNode):
    def emit(self):
        yield self.part('>')


class JSOpGtE(JSNode):
    def emit(self):
        yield self.part('>=')

JSIs = JSOpStrongEq
