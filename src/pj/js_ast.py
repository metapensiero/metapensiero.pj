# -*- coding: utf-8 -*-
# :Project:  pj -- JS ast
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast
from functools import reduce
import json
import re

from .processor.transforming import TargetNode
from .processor.util import delimited


JS_KEYWORDS = set([
    'break', 'case', 'catch', 'continue', 'default', 'delete', 'do', 'else',
    'finally', 'for', 'function', 'if', 'in', 'instanceof', 'new', 'return',
    'switch', 'this', 'throw', 'try', 'typeof', 'var', 'void', 'while', 'with',

    'abstract', 'boolean', 'byte', 'char', 'class', 'const', 'debugger',
    'double', 'enum', 'export', 'extends', 'final', 'float', 'goto',
    'implements', 'import', 'int', 'interface', 'long', 'native', 'package',
    'private', 'protected', 'public', 'short', 'static', 'super',
    'synchronized', 'throws', 'transient', 'volatile'])

#### Misc


class JSNode(TargetNode):
    pass


class JSStatement(JSNode):
    pass


class JSLeftSideUnaryOp(JSNode):
    pass


class JSStatements(JSNode):
    def emit(self, statements):
        for s in statements:
            yield s

class JSPass(JSNode):
    def emit(self):
        return []


class JSCommentBlock(JSNode):
    def emit(self, text):
        assert text.find('*/') == -1
        yield self.part('/* ', text, ' */')

#### Statements


class JSExpressionStatement(JSStatement):
    def emit(self, value):
        yield self.part(value)


class JSVarDeclarer(JSStatement):

    def with_kind(self, kind, keys, values):
        for key in keys:
            assert key not in JS_KEYWORDS, key
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
    def emit(self, keys, values):
        yield from self.with_kind('var', keys, values)


class JSLetStatement(JSVarDeclarer):
    def emit(self, keys, values):
        yield from self.with_kind('let', keys, values)


class JSAugAssignStatement(JSStatement):
    def emit(self, target, op, value):
        yield self.part(target, ' ', op, '= ', value)


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


class JSForeachStatement(JSStatement):
    def emit(self, target, source, body):
        yield self.line(['for (var ', target, ' in ', source, ') {'])
        yield from self.lines(body, indent=True, delim=True)
        yield self.line('}')


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
    def emit(self, obj, key):
        yield self.part('delete ', obj, '[', key, ']')


class JSTryCatchStatement(JSStatement):
    def emit(self, try_body, target, catch_body):
        yield self.line('try {')
        yield from self.lines(try_body, indent=True, delim=True)
        yield self.line(['} catch(', target, ') {'])
        yield from self.lines(catch_body, indent=True, delim=True)
        yield self.line('}')


class JSThrowStatement(JSStatement):
    def emit(self, obj):
        yield self.line(['throw ', obj], delim=True)

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


class JSFunction(JSNode):

    def fargs(self, args):
        result = []
        result.append('(')
        delimited(', ', args, dest=result)
        result.append(') ')
        return result

    def emit(self, name, args, body):
        line = ['function ']
        if name is not None:
            line.append(name)
        line += self.fargs(args)
        line += ['{']
        yield self.line(line)
        yield from self.lines(body, indent=True, delim=True)
        yield self.line('}')


class JSClass(JSNode):

    def emit(self, name, super_, methods):
        line = ['class ', name]
        if super_ is not None:
            line += [' extends ', super_]
        line += [' {']
        yield self.line(line)
        yield from self.lines(methods, indent=True, delim=True)
        yield self.line('}')


class JSClassMember(JSFunction):

    def with_kind(self, kind, args, body):
        line = [kind]
        line += self.fargs(args)
        line += ['{']
        yield self.line(line)
        yield from self.lines(body, indent=True, delim=True)
        yield self.line('}')


class JSClassConstructor(JSClassMember):

    def emit(self, args, body):
        yield from self.with_kind('constructor', args, body)


class JSMethod(JSClassMember):

    def emit(self, name, args, body):
        yield from self.with_kind(name, args, body)


class JSAssignmentExpression(JSNode):
    def emit(self, left, right):
        yield self.part(left, ' = ', right)


class JSIfExp(JSNode):
    def emit(self, test, body, orelse):
        yield self.part('(', test, ' ? ', body, ' : ', orelse, ')')


class JSCall(JSNode):
    def emit(self, func, args):
        arr = [func, '(']
        delimited(', ', args, dest=arr)
        arr.append(')')
        yield self.part(*arr)


class JSNewCall(JSNode):
    def emit(self, func, args):
        arr = ['new ', func, '(']
        delimited(', ', args, dest=arr)
        arr.append(')')
        yield self.part(*arr)


class JSAttribute(JSNode):
    def emit(self, obj, s):
        assert re.search(r'^[a-zA-Z_][a-zA-Z_0-9]*$', s)
        assert s not in JS_KEYWORDS
        yield self.part(obj, '.', s)


class JSSubscript(JSNode):
    def emit(self, obj, key):
        yield self.part(obj, '[', key, ']')


class JSBinOp(JSNode):
    def emit(self, left, op, right):
        yield self.part('(', left, ' ', op, ' ', right, ')')


class JSUnaryOp(JSNode):
    def emit(self, op, right):
        assert isinstance(op, JSLeftSideUnaryOp)
        yield self.part('(', op, ' ', right, ')')

#### Atoms


class JSNum(JSNode):
    def emit(self, x):
        yield self.part(str(x))


class JSStr(JSNode):
    def emit(self, s):
        yield self.part(json.dumps(s))


class JSName(JSNode):
    def emit(self, name):
        assert name not in JS_KEYWORDS, name
        yield self.part(name)


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
