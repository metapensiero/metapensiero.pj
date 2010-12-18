
import ast

from pyxc.importing import SourcePath, orderedModules
from pyxc.transforming import Transformer
from pyxc.util import topLevelNamesInBody

import pj.js_ast
import pj.transformations


#### Code to Code
def codeToCode(py):
    
    t = Transformer(pj.transformations, pj.js_ast.JSStatements)
    jsAst = t.transformCode(py)
    js = '%s\n%s' % ('\n'.join(t.snippets), str(jsAst))
    
    names = set(topLevelNamesInBody(ast.parse(py).body))
    if len(names) > 0:
        js = 'var %s;\n\n%s' % (
            ', '.join(names),
            js)
    
    return js


#### Build Bundle
def buildBundle(mainModule, path=None, includeSource=False, prependJs=None):
    
    assert path
    
    t = Transformer(pj.transformations, pj.js_ast.JSStatements)
    sourcePath = SourcePath(path)
    modules = orderedModules(sourcePath, mainModule)
    
    jsArr = []
    topLevelNames = set()
    
    sourceDict = {}
    
    for module in modules:
        codePath = sourcePath.pathForModule(module)
        with open(codePath, 'rb') as f:
            
            py = str(f.read(), 'utf-8')
            
            sourceDict[module] = {
                'path': codePath,
                'code': py,
                'module': module,
            }
            
            if codePath.endswith('.js'):
                js = py
            
            else:
                
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
    
    jsPrefix = ''.join([
                    (prependJs + '\n\n') if prependJs is not None else '',
                    '(function(){\n\n',
                    '\n'.join(t.snippets), '\n\n',
                    varJs, '\n\n'])
    
    js = ''.join([
                    jsPrefix,
                    ''.join(jsArr),
                    '\n\n})();'])
    
    info = {
        'js': js,
    }
    
    if includeSource:
        info['sourceDict'] = sourceDict
    
    return info


