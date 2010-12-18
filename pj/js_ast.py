
# To learn what pyxc is doing for you behind the scenes,
# read [pyxc.org/transformations/](http://pyxc.org/transformations/)

import ast, json, re
from functools import reduce

from pyxc.transforming import TargetNode
from pyxc.util import delimitedList


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
        return delimitedList(';\n', statements, delimAtEnd=True)

class JSPass(JSNode):
    def emit(self):
        return ['']

class JSCommentBlock(JSNode):
    def emit(self, text):
        assert text.find('*/') == -1
        return ['/* ', text, ' */']

#### Statements

class JSExpressionStatement(JSStatement):
    def emit(self, value):
        return [value]

class JSVarStatement(JSStatement):
    def emit(self, keys, values):
        for key in keys:
            assert key not in JS_KEYWORDS, key
        assert len(keys) > 0
        assert len(keys) == len(values)
        
        arr = ['var ']
        for i in range(len(keys)):
            if i > 0:
                arr.append(', ')
            arr.append(keys[i])
            if values[i] is not None:
                arr.append(' = ')
                arr.append(values[i])
        return arr

class JSAugAssignStatement(JSStatement):
    def emit(self, target, op, value):
        return [target, ' ', op, '= ', value]

class JSIfStatement(JSStatement):
    def emit(self, test, body, orelse):
        
        arr = ['if (', test, ') {']
        delimitedList(';', body, dest=arr)
        arr.append('}')
        
        if orelse:
            arr.append('else {')
            delimitedList(';', orelse, dest=arr)
            arr.append('}')
        
        return arr

class JSWhileStatement(JSStatement):
    def emit(self, test, body):
        arr = ['while (', test, ') {']
        delimitedList(';', body, dest=arr)
        arr.append('}')
        return arr

class JSForStatement(JSStatement):
    def emit(self, left, test, right, body):
        arr = ['for (', left, '; ', test, '; ', right, ') {']
        delimitedList(';', body, dest=arr)
        arr.append('}')
        return arr

class JSForeachStatement(JSStatement):
    def emit(self, target, source, body):
        arr = ['for (var ', target, ' in ', source, ') {']
        delimitedList(';', body, dest=arr)
        arr.append('}')
        return arr

class JSReturnStatement(JSStatement):
    def emit(self, value):
        if value:
            return ['return ', value]
        else:
            return ['return']

class JSBreakStatement(JSStatement):
    def emit(self):
        return ['break']

class JSContinueStatement(JSStatement):
    def emit(self):
        return ['continue']

class JSDeleteStatement(JSStatement):
    def emit(self, obj, key):
        return ['delete ', obj, '[', key, ']']

class JSTryCatchStatement(JSStatement):
    def emit(self, tryBody, target, catchBody):
        arr = ['try {']
        delimitedList(';', tryBody, dest=arr)
        arr.append('} catch(')
        arr.append(target)
        arr.append(') {')
        delimitedList(';', catchBody, dest=arr)
        arr.append('}')
        return arr

class JSThrowStatement(JSStatement):
    def emit(self, obj):
        return ['throw ', obj]

#### Expressions

class JSList(JSNode):
    def emit(self, elts):
        arr = ['[']
        delimitedList(', ', elts, dest=arr)
        arr.append(']')
        return arr

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
        return arr

class JSFunction(JSNode):
    def emit(self, name, args, body):
        arr = ['(function ']
        if name is not None:
            arr.append(name)
        arr.append('(')
        delimitedList(', ', args, dest=arr)
        arr.append('){')
        delimitedList(';\n', body, dest=arr)
        arr.append('})')
        return arr

class JSAssignmentExpression(JSNode):
    def emit(self, left, right):
        return ['(', left, ' = ', right, ')']

class JSIfExp(JSNode):
    def emit(self, test, body, orelse):
        return ['(', test, ' ? ', body, ' : ', orelse, ')']

class JSCall(JSNode):
    def emit(self, func, args):
        arr = ['(', func, '(']
        delimitedList(', ', args, dest=arr)
        arr.append('))')
        return arr

class JSNewCall(JSNode):
    def emit(self, func, args):
        arr = ['(new ', func, '(']
        delimitedList(', ', args, dest=arr)
        arr.append('))')
        return arr

class JSAttribute(JSNode):
    def emit(self, obj, s):
        assert re.search(r'^[a-zA-Z_][a-zA-Z_0-9]*$', s)
        assert s not in JS_KEYWORDS
        return [obj, '.', s]

class JSSubscript(JSNode):
    def emit(self, obj, key):
        return [obj, '[', key, ']']

class JSBinOp(JSNode):
    def emit(self, left, op, right):
        return ['(', left, ' ', op, ' ', right, ')']

class JSUnaryOp(JSNode):
    def emit(self, op, right):
        assert isinstance(op, JSLeftSideUnaryOp)
        return ['(', op, ' ', right, ')']

#### Atoms

class JSNum(JSNode):
    def emit(self, x):
        return [str(x)]

class JSStr(JSNode):
    def emit(self, s):
        return [json.dumps(s)]

class JSName(JSNode):
    def emit(self, name):
        assert name not in JS_KEYWORDS, name
        return [name]

class JSThis(JSNode):
    def emit(self):
        return ['this']

class JSTrue(JSNode):
    def emit(self):
        return ['true']

class JSFalse(JSNode):
    def emit(self):
        return ['false']

class JSNull(JSNode):
    def emit(self):
        return ['null']

#### Ops

class JSOpIn(JSNode):
    def emit(self):
        return ['in']

class JSOpAnd(JSNode):
    def emit(self):
        return ['&&']

class JSOpOr(JSNode):
    def emit(self):
        return ['||']

class JSOpNot(JSLeftSideUnaryOp):
    def emit(self):
        return ['!']

class JSOpInstanceof(JSNode):
    def emit(self):
        return ['instanceof']

class JSOpTypeof(JSLeftSideUnaryOp):
    def emit(self):
        return ['typeof']

class JSOpAdd(JSNode):
    def emit(self):
        return ['+']

class JSOpSub(JSNode):
    def emit(self):
        return ['-']

class JSOpMult(JSNode):
    def emit(self):
        return ['*']

class JSOpDiv(JSNode):
    def emit(self):
        return ['/']

class JSOpMod(JSNode):
    def emit(self):
        return ['%']

class JSOpRShift(JSNode):
    def emit(self):
        return ['>>']

class JSOpLShift(JSNode):
    def emit(self):
        return ['<<']

class JSOpBitXor(JSNode):
    def emit(self):
        return ['^']

class JSOpBitAnd(JSNode):
    def emit(self):
        return ['&']

class JSOpBitOr(JSNode):
    def emit(self):
        return ['|']

class JSOpInvert(JSLeftSideUnaryOp):
    def emit(self):
        return ['~']

class JSOpStrongEq(JSNode):
    def emit(self):
        return ['===']

class JSOpStrongNotEq(JSNode):
    def emit(self):
        return ['!==']

class JSOpLt(JSNode):
    def emit(self):
        return ['<']

class JSOpLtE(JSNode):
    def emit(self):
        return ['<=']

class JSOpGt(JSNode):
    def emit(self):
        return ['>']

class JSOpGtE(JSNode):
    def emit(self):
        return ['>=']

