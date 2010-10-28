
from pyxc.util import usingPython3
assert usingPython3()

import sys, os, ast
from pyxc.util import rfilter, parentOf, randomToken

from pyxc.pyxc_exceptions import NoTransformationForNode

#### TargetNode

class TargetNode:
    
    def __init__(self, *args):
        self.args = args
    
    def __str__(self):
        args = []
        for y in self.transformedArgs:
            if isinstance(y, list) or isinstance(y, tuple):
                args.append([str(child) for child in y])
            else:
                args.append(str(y))
        return self.emit(*args)

#### Transformer

class Transformer:
    
    def __init__(self, parentModule, statementsClass):
        self.transformationsDict = loadTransformationsDict(parentModule)
        self.statementsClass = statementsClass
        self.snippets = set()
    
    def transformCode(self, py):
        
        top = ast.parse(py)
        body = top.body
        
        self.node_parent_map = buildNodeParentMap(top)
        
        transformedBody = [self._transformNode(x) for x in body]
        result = self.statementsClass(transformedBody)
        self._finalizeTargetNode(result)
        
        self.node_parent_map = None
        
        return result
    
    def parentOf(self, node):
        return self.node_parent_map.get(node)
    
    def firstAncestorSubclassing(self, node, cls):
        parent = self.parentOf(node)
        if parent is not None:
            if isinstance(parent, cls):
                return parent
            else:
                return self.firstAncestorSubclassing(parent, cls)
    
    def newName(self):
        #LATER: generate better names
        return randomToken(20)
    
    def addSnippet(self, targetCode):
        self.snippets.add(targetCode)
    
    def _transformNode(self, x):
        
        if isinstance(x, list) or isinstance(x, tuple):
            return [self._transformNode(child) for child in x]
        
        elif isinstance(x, ast.AST):
            for t in self.transformationsDict.get(x.__class__.__name__, []):
                y = t(self, x)
                if y is not None:
                    self._finalizeTargetNode(y)
                    return y
            raise NoTransformationForNode(repr(x))
        
        elif isinstance(x, TargetNode):
            self._finalizeTargetNode(x)
            return x
        
        else:
            # e.g. an integer
            return x
    
    def _finalizeTargetNode(self, y):
        y.transformedArgs = [self._transformNode(arg) for arg in y.args]
        y.transformer = self


#### Helpers

def getPythonAstNames():
    #LATER: do this properly
    return rfilter(r'[A-Z][a-zA-Z]+', dir(ast))


def loadTransformationsDict(parentModule):
    # transformationsDict = {
    #     'NodeName': [...transformation functions...]
    # }
    d = {}
    astNames = list(getPythonAstNames())
    filenames = rfilter(
                            r'^[^.]+\.py$',
                            os.listdir(parentOf(parentModule.__file__)))
    for filename in filenames:
        if filename != '__init__.py':
            modName = 'pj.transformations.%s' % filename.split('.')[0]
            __import__(modName)
            mod = sys.modules[modName]
            for name in dir(mod):
                if name in astNames:
                    assert name not in d
                    value = getattr(mod, name)
                    if not isinstance(value, list) or isinstance(value, tuple):
                        value = [value]
                    d[name] = value
    return d


def buildNodeParentMap(top):
    
    node_parent_map = {}
    
    def _processNode(node):
        for k in node._fields:
            x = getattr(node, k)
            if not (isinstance(x, list) or isinstance(x, tuple)):
                x = [x]
            for y in x:
                if isinstance(y, ast.AST):
                    node_parent_map[y] = node
                    _processNode(y)
    
    _processNode(top)
    
    return node_parent_map

