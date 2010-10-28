
import ast
from pj.js_ast import *

#### TryExcept, Raise
# Example:
#<pre>try:
#    raise EpicFail('omg noes!')
#except Exception as NAME:
#    ...</pre>
# becomes
#<pre>try {
#    throw {'name': 'EpicFail', 'message': 'omg noes!'};
#}
#catch(NAME) {
#    ...
#}</pre>
# 
# This is the only form supported so far.
def TryExcept(t, x):
    assert not x.orelse
    assert len(x.handlers) == 1
    assert isinstance(x.handlers[0].type, ast.Name)
    assert x.handlers[0].type.id == 'Exception'
    assert x.handlers[0].name
    
    NAME = x.handlers[0].name
    TRY_BODY = x.body
    CATCH_BODY = x.handlers[0].body
    
    return JSTryCatchStatement(
                TRY_BODY,
                NAME,
                CATCH_BODY)


def Raise(t, x):
    
    if isinstance(x.exc, ast.Name):
        name = x.exc.id
        message = ''
    else:
        assert isinstance(x.exc, ast.Call)
        assert isinstance(x.exc.func, ast.Name)
        assert len(x.exc.args) == 1
        assert isinstance(x.exc.args[0], ast.Str)
        assert all((not x) for x in (
            x.exc.keywords, x.exc.starargs, x.exc.kwargs))
        name = x.exc.func.id
        message = x.exc.args[0].s
    
    return JSThrowStatement(
                JSDict(
                    [JSStr('name'), JSStr('message')],
                    [JSStr(name), JSStr(message)]))

