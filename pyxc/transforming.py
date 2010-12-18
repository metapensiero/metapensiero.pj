
from pyxc.util import usingPython3
assert usingPython3()

import sys, os, ast, json, hashlib
from pyxc.util import rfilter, parentOf, randomToken

from pyxc.pyxc_exceptions import NoTransformationForNode

#### TargetNode

class TargetNode:
    
    def __init__(self, *args):
        self.args = args
    
    def __str__(self):
        return ''.join(
                    str(x) for x in
                        self.emit(*self.transformedArgs))


#### SourceMap

class SourceMap:
    
    def __init__(self, fileString, nextMappingId=0):
        
        self.fileString = fileString
        
        self.nextMappingId = nextMappingId
        self.node_mappingId_map = {}
        self.mappings = []
        
        self.linemaps = [[]]
        self.strings = []
    
    def getCode(self):
        return ''.join(self.strings)
    
    def handleNode(self, node, parentMappingId=0):
        
        mappingId = self.mappingIdForNode(node)
        if mappingId is None:
            mappingId = parentMappingId
        
        arr = node.emit(*node.transformedArgs)
        for x in arr:
            if isinstance(x, str):
                if x:
                    # Store the string
                    self.strings.append(x)
                    
                    # Update self.linemaps
                    linemap = self.linemaps[-1]
                    for c in x:
                        linemap.append(mappingId)
                        if c == '\n':
                            linemap = []
                            self.linemaps.append(linemap)
            else:
                assert isinstance(x, TargetNode)
                self.handleNode(x, parentMappingId=mappingId)
    
    def mappingIdForNode(self, node):
        if node in self.node_mappingId_map:
            return self.node_mappingId_map[node]
        else:
            lineno = getattr(node.pyNode, 'lineno', None)
            col_offset = getattr(node.pyNode, 'col_offset', None)
            if (lineno is None) or (col_offset is None):
                return None
            else:
                mappingId = self.nextMappingId
                self.nextMappingId += 1
                self.node_mappingId_map[node] = mappingId
                self.mappings.append([self.fileString, lineno, col_offset])
                return mappingId


def exportSourceMap(linemaps, mappings, sourceDict):
    
    # Get filekeys from mappings
    filekeys = []
    filekeysSet = set()
    for tup in mappings:
        k = tup[0]
        if k not in filekeysSet:
            filekeysSet.add(k)
            filekeys.append(k)
    
    arr = ['/** Begin line maps. **/{ "file" : "", "count": %d }\n' % len(filekeys)]
    
    for linemap in linemaps:
        arr.append(json.dumps(linemap, separators=(',', ':')) + '\n')
    
    arr.append('/** Begin file information. **/\n')
    for k in filekeys:
        sourceInfo = sourceDict[k]
        arr.append('%s\n' % json.dumps([{
            'module': sourceInfo['module'],
            'sha1': hashlib.sha1(sourceInfo['code'].encode('utf-8')).hexdigest(),
            'path': sourceInfo['path'],
            'name': sourceInfo['path'].split('/')[-1],
            'k': k,
        }]))
    arr.append('/** Begin mapping definitions. **/\n')
    
    for mapping in mappings:
        arr.append(json.dumps(mapping, separators=(',', ':')) + '\n')
    
    return ''.join(arr)


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

