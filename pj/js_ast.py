
# To learn what pyxc is doing for you behind the scenes,
# read [pyxc.org/transformations/](http://pyxc.org/transformations/)

import ast, json, re
from functools import reduce

from pyxc.transforming import TargetNode

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
        return ''.join((x + ';\n') for x in statements)

class JSPass(JSNode):
    def emit(self):
        return ''

class JSCommentBlock(JSNode):
    def emit(self, text):
        assert text.find('*/') == -1
        return '/* %s */' % text

#### Statements

class JSExpressionStatement(JSStatement):
    def emit(self, value):
        return value

class JSVarStatement(JSStatement):
    def emit(self, keys, values):
        for key in keys:
            assert key not in JS_KEYWORDS, key
        assert len(keys) > 0
        assert len(keys) == len(values)
        return 'var %s' % ', '.join(
                    ('%s = %s' % (keys[i], values[i])) if self.transformedArgs[1][i] is not None else ('%s' % (keys[i]))
                    for i in range(len(keys)))

class JSAugAssignStatement(JSStatement):
    def emit(self, target, op, value):
        return '%s %s= %s' % (target, op, value)

class JSIfStatement(JSStatement):
    def emit(self, test, body, orelse):
        if self.transformedArgs[2]:
            return 'if (%s) {%s} else {%s}' % (
                        test, ';'.join(body), ';'.join(orelse))
        else:
            return 'if (%s) {%s}' % (test, ';'.join(body))

class JSWhileStatement(JSStatement):
    def emit(self, test, body):
        return 'while (%s) {%s}' % (test, ';'.join(body))

class JSForStatement(JSStatement):
    def emit(self, left, test, right, body):
        return 'for (%s; %s; %s) {%s}' % (left, test, right, ';\n'.join(body))

class JSForeachStatement(JSStatement):
    def emit(self, target, source, body):
        return 'for (var %s in %s) {%s}' % (target, source, ';\n'.join(body))

class JSReturnStatement(JSStatement):
    def emit(self, value):
        if self.transformedArgs[0]:
            return 'return %s' % value
        else:
            return 'return'

class JSBreakStatement(JSStatement):
    def emit(self):
        return 'break'

class JSContinueStatement(JSStatement):
    def emit(self):
        return 'continue'

class JSDeleteStatement(JSStatement):
    def emit(self, obj, key):
        return 'delete %s[%s]' % (obj, key)

class JSTryCatchStatement(JSStatement):
    def emit(self, tryBody, target, catchBody):
        return 'try {%s} catch(%s) {%s}' % (
                    ';\n'.join(tryBody),
                    target,
                    ';\n'.join(catchBody))

class JSThrowStatement(JSStatement):
    def emit(self, exceptionObject):
        return 'throw %s' % exceptionObject

#### Expressions

class JSList(JSNode):
    def emit(self, elts):
        return '[%s]' % ', '.join(elts)

class JSDict(JSNode):
    def emit(self, keys, values):
        return '{%s}' % ', '.join(
                ('%s: %s' % (k, v))
                for k, v in zip(keys, values))

class JSFunction(JSNode):
    def emit(self, name, args, body):
        return '(function %s(%s){%s})' % (
                        '' if self.transformedArgs[0] is None else name,
                        ', '.join(args),
                        ';\n'.join(body))

class JSAssignmentExpression(JSNode):
    def emit(self, left, right):
        return '(%s = %s)' % (left, right)

class JSIfExp(JSNode):
    def emit(self, test, body, orelse):
        return '(%s ? %s : %s)' % (test, body, orelse)

class JSCall(JSNode):
    def emit(self, func, args):
        return '(%s(%s))' % (func, ', '.join(args))

class JSNewCall(JSNode):
    def emit(self, func, args):
        return '(new %s(%s))' % (func, ', '.join(args))

class JSAttribute(JSNode):
    def emit(self, obj, s):
        assert re.search(r'^[a-zA-Z_][a-zA-Z_0-9]*$', s)
        assert s not in JS_KEYWORDS
        return '%s.%s' % (obj, s)

class JSSubscript(JSNode):
    def emit(self, obj, key):
        return '%s[%s]' % (obj, key)

class JSBinOp(JSNode):
    def emit(self, left, op, right):
        return '(%s %s %s)' % (left, op, right)

class JSUnaryOp(JSNode):
    def emit(self, op, right):
        assert isinstance(self.transformedArgs[0], JSLeftSideUnaryOp)
        return '(%s %s)' % (op, right)

#### Atoms

class JSNum(JSNode):
    def emit(self, x):
        return str(x)

class JSStr(JSNode):
    def emit(self, s):
        return json.dumps(s)

class JSName(JSNode):
    def emit(self, name):
        assert name not in JS_KEYWORDS, name
        return '%s' % name

class JSThis(JSNode):
    def emit(self):
        return 'this'

class JSTrue(JSNode):
    def emit(self):
        return 'true'

class JSFalse(JSNode):
    def emit(self):
        return 'false'

class JSNull(JSNode):
    def emit(self):
        return 'null'

#### Ops

class JSOpIn(JSNode):
    def emit(self):
        return 'in'

class JSOpAnd(JSNode):
    def emit(self):
        return '&&'

class JSOpOr(JSNode):
    def emit(self):
        return '||'

class JSOpNot(JSLeftSideUnaryOp):
    def emit(self):
        return '!'

class JSOpInstanceof(JSNode):
    def emit(self):
        return 'instanceof'

class JSOpTypeof(JSLeftSideUnaryOp):
    def emit(self):
        return 'typeof'

class JSOpAdd(JSNode):
    def emit(self):
        return '+'

class JSOpSub(JSNode):
    def emit(self):
        return '-'

class JSOpMult(JSNode):
    def emit(self):
        return '*'

class JSOpDiv(JSNode):
    def emit(self):
        return '/'

class JSOpMod(JSNode):
    def emit(self):
        return '%'

class JSOpRShift(JSNode):
    def emit(self):
        return '>>'

class JSOpLShift(JSNode):
    def emit(self):
        return '<<'

class JSOpBitXor(JSNode):
    def emit(self):
        return '^'

class JSOpBitAnd(JSNode):
    def emit(self):
        return '&'

class JSOpBitOr(JSNode):
    def emit(self):
        return '|'

class JSOpInvert(JSLeftSideUnaryOp):
    def emit(self):
        return '~'

class JSOpStrongEq(JSNode):
    def emit(self):
        return '==='

class JSOpStrongNotEq(JSNode):
    def emit(self):
        return '!=='

class JSOpLt(JSNode):
    def emit(self):
        return '<'

class JSOpLtE(JSNode):
    def emit(self):
        return '<='

class JSOpGt(JSNode):
    def emit(self):
        return '>'

class JSOpGtE(JSNode):
    def emit(self):
        return '>='

