import ast

from pyxc.importing import SourcePath, orderedModules
from pyxc.transforming import Transformer, SourceMap, exportSourceMap
from pyxc.util import body_top_names

import pj.js_ast
import pj.transformations


#### Code to Code
def codeToCode(py):

    t = Transformer(pj.transformations, pj.js_ast.JSStatements)
    jsAst = t.transform_code(py)
    js = '%s\n%s' % ('\n'.join(t.snippets), str(jsAst))

    names = set(body_top_names(ast.parse(py).body))
    if len(names) > 0:
        js = 'var %s;\n\n%s' % (
            ', '.join(names),
            js)

    return js


#### Build Bundle
def buildBundle(mainModule, path=None, createSourceMap=False, includeSource=False, prependJs=None):

    assert path

    t = Transformer(pj.transformations, pj.js_ast.JSStatements)
    sourcePath = SourcePath(path)
    modules = orderedModules(sourcePath, mainModule)

    jsArr = []
    topLevelNames = set()

    linemaps = []
    mappings = []

    sourceDict = {}

    i = 0
    for module in modules:
        fileKey = str(i)
        i += 1
        codePath = sourcePath.pathForModule(module)
        with open(codePath, 'rb') as f:

            py = str(f.read(), 'utf-8')

            sourceDict[fileKey] = {
                'path': codePath,
                'code': py,
                'module': module,
            }

            if codePath.endswith('.js'):
                js = py

            else:

                # Load the top-level names and confirm they're distinct
                for name in body_top_names(ast.parse(py).body):
                    assert name not in topLevelNames
                    topLevelNames.add(name)

                # py &rarr; js
                jsAst = t.transform_code(py)
                if createSourceMap:

                    sm = SourceMap(fileKey, nextMappingId=len(mappings))
                    sm.handleNode(jsAst)

                    js = sm.getCode() + '\n'

                    assert len(sm.linemaps) == len(js.split('\n')) - 1

                    linemaps += sm.linemaps
                    mappings += sm.mappings

                else:
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

    jsSuffix = '\n\n})();'

    linemaps = (
                    [([-1] * (len(s) + 2)) for s in jsPrefix.split('\n')[:-1]] +
                    linemaps[:-1] +
                    [([-1] * (len(s) + 2)) for s in jsPrefix.split('\n')])

    js = ''.join([
                    jsPrefix,
                    ''.join(jsArr),
                    jsSuffix])

    info = {
        'js': js,
    }

    if createSourceMap:
        info['sourceMap'] = exportSourceMap(linemaps, mappings, sourceDict)

    if includeSource:
        info['sourceDict'] = dict(
                                    (
                                        sourceDict[k]['module'],
                                        sourceDict[k])
                                    for k in sourceDict)

    return info
