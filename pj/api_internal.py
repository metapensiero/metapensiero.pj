
import ast

from pyxc.importing import SourcePath, orderedModules
from pyxc.transforming import Transformer
from pyxc.analysis import topLevelNamesInBody

import pj.js_ast
import pj.transformations


#### Code to Code
def codeToCode(py):
    t = Transformer(pj.transformations, pj.js_ast.JSStatements)
    jsAst = t.transformCode(py)
    js = '%s\n%s' % ('\n'.join(t.snippets), str(jsAst))
    return js


#### Build Bundle
def buildBundle(mainModule, path=None):
    
    assert path
    
    t = Transformer(pj.transformations, pj.js_ast.JSStatements)
    sourcePath = SourcePath(path)
    modules = orderedModules(sourcePath, mainModule)
    
    jsArr = []
    topLevelNames = set()
    for module in modules:
        codePath = sourcePath.pathForModule(module)
        with open(codePath, 'rb') as f:
            py = f.read()
            
            # Load the top-level names and confirm they're distinct
            for name in topLevelNamesInBody(ast.parse(py).body):
                assert name not in topLevelNames
                topLevelNames.add(name)
            
            # py &rarr; js
            jsAst = t.transformCode(py)
            js = str(jsAst)
            jsArr.append(js)
    
    if len(topLevelNames) > 0:
        varJs = 'var %s;' % ', '.join(list(topLevelNames))
    else:
        varJs = ''
    
    js = '''(function(){
  %s
  %s
  %s
})();''' % (
                '\n'.join(t.snippets),
                varJs,
                '\n'.join(jsArr))
    
    return js


