
import ast
from pj.js_ast import *

from pyxc.analysis import localNamesInBody


#### ClassDef
#
# The generated code is the same as [what CoffeeScript generates](http://jashkenas.github.com/coffee-script/#classes).


#<pre>class Animal:                                      ---->
#    def __init__(self, name):
#        self.name = name</pre>
'''
var Animal = function(name) {
    this.name = name;
    return this;
}
'''
#<pre>class TalkingAnimal(Animal):                       ---->
#    def __init__(self, name, catchphrase):
#        super(name)
#        self.catchphrase = catchphrase
#    def caption(self):
#        return self.name + ' sez "' + self.catchphrase + '"'</pre>
'''
var TalkingAnimal = function() {
    this.__super__.__init__.call(this, name);
    this.catchphrase = catchphrase;
    return this
}
__extends(TalkingAnimal, Animal);
TalkingAnimal.prototype.caption = function() {
    alert(this.name + ' sez "' + this.catchphrase + '"');
}
'''
#<pre>class Kitteh(TalkingAnimal):                       ---->
#    def __init__(self, name):
#        super(name, 'OH HAI')
#    def caption(self):
#        return super() + '!!!'</pre>
'''
var Kitteh = function() {
    this.__super__.__init__.call(this, name, "OH HAI");
    return this;
};
__extends(Kitteh, TalkingAnimal);
Kitteh.prototype.caption = function() {
    return this.__super__.caption + "!!!";
};
'''

def ClassDef(t, x):
    
    assert not x.keywords, x.keywords
    assert not x.starargs, x.starargs
    assert not x.kwargs, x.kwargs
    assert not x.decorator_list, x.decorator_list
    
    # If the bundle you're building contains any ClassDef,
    # this snippet ([from CoffeeScript](http://jashkenas.github.com/coffee-script/#classes)) will be included once at the top:
    #
    # <pre>var __extends = function(child, parent) {
    #    var ctor = function(){};
    #    ctor.prototype = parent.prototype;
    #    child.prototype = new ctor();
    #    child.prototype.__init__ = child;
    #    if (typeof parent.extended === "function") {
    #        parent.extended(child);
    #    }
    #    child.__super__ = parent.prototype;
    # };</pre>
    
    extends_helper_name = '__extends'
    t.addSnippet('''var %s = function(child, parent) {
    var ctor = function(){};
    ctor.prototype = parent.prototype;
    child.prototype = new ctor();
    child.prototype.__init__ = child;
    if (typeof parent.extended === "function") {
         parent.extended(child);
    }
    child.__super__ = parent.prototype;
};''' % extends_helper_name)
    
    
    NAME_STRING = x.name
    BODY = x.body
    if len(x.bases) > 0:
        assert len(x.bases) == 1
        assert isinstance(x.bases[0], ast.Name)
        SUPERCLASS_STRING = x.bases[0].id
    else:
        SUPERCLASS_STRING = None
    
    # Enforced restrictions:
    
    # * The class body must consist of nothing but FunctionDefs
    for node in BODY:
        assert isinstance(node, ast.FunctionDef)
    
    # * Each FunctionDef must have self as its first arg
    for node in BODY:
        argNames = [arg.arg for arg in node.args.args]
        assert len(argNames) > 0 and argNames[0] == 'self'
    
    # * (You need \_\_init\_\_) and (it must be the first FunctionDef)
    assert len(BODY) > 0
    INIT = BODY[0]
    assert str(INIT.name) == '__init__'
    
    # * \_\_init\_\_ may not contain a return statement
    INIT_ARGS = [arg.arg for arg in INIT.args.args]
    INIT_BODY = INIT.body
    for stmt in ast.walk(INIT):
        assert not isinstance(stmt, ast.Return)
    
    #<pre>var Kitteh = function(...args...) {
    #    ...__init__ body...
    #    return this;
    #};</pre>
    statements = [
        JSExpressionStatement(
            JSAssignmentExpression(
                JSName(NAME_STRING),
                INIT))]
    
    #<pre>__extends(Kitteh, TalkingAnimal);</pre>
    if SUPERCLASS_STRING is not None:
        statements.append(
            JSExpressionStatement(
                JSCall(
                    JSName(extends_helper_name),
                    [
                        JSName(NAME_STRING),
                        JSName(SUPERCLASS_STRING)])))
    
    # Now for the methods:
    for METHOD in BODY:
        if str(METHOD.name) != '__init__':
            
            #<pre>Kitteh.prototype.caption = function(...){...};
            statements.append(
                JSExpressionStatement(
                    JSAssignmentExpression(
                        JSAttribute(# Kitteh.prototype.caption
                            JSAttribute(# Kitteh.prototype
                                JSName(NAME_STRING),
                                'prototype'),
                            str(METHOD.name)),
                        METHOD)))
    
    return JSStatements(statements)


#### Call_super
def Call_super(t, x):
    if (
            isinstance(x.func, ast.Name) and
            x.func.id == 'super'):
        
        # Are we in a FuncDef and is it a method?
        METHOD = t.firstAncestorSubclassing(x, ast.FunctionDef)
        if METHOD and isinstance(t.parentOf(METHOD), ast.ClassDef):
            
            cls = t.parentOf(METHOD)
            assert len(cls.bases) == 1
            assert isinstance(cls.bases[0], ast.Name)
            SUPERCLASS_STRING = cls.bases[0].id
            CLASS_STRING = cls.name
            
            # <code>super(...)</code> &rarr; <code>SUPERCLASS.call(this, ...)</code>
            if METHOD.name == '__init__':
                return JSCall(
                            JSAttribute(
                                JSName(SUPERCLASS_STRING),
                                'call'),
                            [JSThis()] + x.args)
            
            # <code>super(...)</code> &rarr; <code>CLASSNAME.__super__.METHODNAME.call(this, ...)</code>
            else:
                return JSCall(
                            JSAttribute(
                                JSAttribute(
                                    JSAttribute(
                                        JSName(CLASS_STRING),
                                        '__super__'),
                                    METHOD.name),
                                'call'),
                            [JSThis()] + x.args)


#### FunctionDef
def FunctionDef(t, x):
    
    assert not x.decorator_list
    assert not any(getattr(x.args, k) for k in [
            'vararg', 'varargannotation', 'kwonlyargs', 'kwarg',
            'kwargannotation', 'defaults', 'kw_defaults'])
    
    NAME = x.name
    ARGS = [arg.arg for arg in x.args.args]
    BODY = x.body
    
    # <code>var ...local vars...</code>
    localVars = list(set(localNamesInBody(BODY)))
    if len(localVars) > 0:
        BODY = [JSVarStatement(
                            localVars,
                            [None] * len(localVars))] + BODY
    
    # If x is a method
    if isinstance(t.parentOf(x), ast.ClassDef):
        
        # Skip <code>self</code>
        ARGS = ARGS[1:]
        
        # Add <code>return this;</code> if we're <code>__init__</code>
        if NAME == '__init__':
            BODY =  BODY + [JSReturnStatement(
                                JSThis())]
        
        return JSFunction(
                            str(NAME),
                            ARGS,
                            BODY)
    
    # x is a function
    else:
        return JSExpressionStatement(
                    JSAssignmentExpression(
                        str(NAME),
                        JSFunction(
                                        str(NAME),
                                        ARGS,
                                        BODY)))


