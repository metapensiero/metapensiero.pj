# Most of these items also appear in
# [github.com/andrewschaaf/util](http://github.com/andrewschaaf/util)

import json, sys, traceback, re, random, copy, ast
import os, subprocess
from subprocess import check_call, call


def usingPython3():
    return sys.version_info[0] == 3


def parentOf(path):
    return '/'.join(path.rstrip('/').split('/')[:-1])



def topLevelNamesInBody(body):
    names = set()
    for x in body:
        names |= namesInNode(x)
    return names


def localNamesInBody(body):
    names = set()
    for node in body:
        names |= namesInNode(node)
        for x in ast.walk(node):
            names |= namesInNode(x)
    return names


def namesInNode(x):
    names = set()
    if isinstance(x, ast.Assign):
        for target in x.targets:
            if isinstance(target, ast.Name):
                names.add(target.id)
    elif (
            isinstance(x, ast.FunctionDef) or
            isinstance(x, ast.ClassDef)):
        names.add(x.name)
    return names



def exceptionRepr(exc_info=None):
    
    if usingPython3():
        from io import StringIO
    else:
        from StringIO import StringIO
    
    if not exc_info:
        exc_info = sys.exc_info()
    f = StringIO()
    traceback.print_exception(exc_info[0], exc_info[1], exc_info[2], file=f)
    return f.getvalue()


# Write a JSON representation of the exception to stderr for
# the script that's invoking us (e.g. pj.api under Python 2)
def writeExceptionJsonAndDie(e):
    sys.stderr.write('%s\n' % json.dumps({
        'name': e.__class__.__name__,
        'message': exceptionRepr(),
    }))
    sys.exit(1)


def randomToken(n):
    while True:
        token = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(n))
        if not token.isdigit():
            return token


class CyclicGraphError(Exception): pass


class DirectedGraph:
    
    def __init__(self):
        self._graph = {}
    
    def addArc(self, x, y):
        if x not in self._graph:
            self._graph[x] = set()
        if y not in self._graph:
            self._graph[y] = set()
        self._graph[x].add(y)
    
    @property
    def topologicalOrdering(self):
        
        def topologicalOrderingDestructive(d):
            
            if len(d) == 0:
                return []
            
            possibleInitialNodes = set(d.keys())
            for k, v in d.items():
                if len(v) > 0:
                    possibleInitialNodes.discard(k)
            if len(possibleInitialNodes) == 0:
                raise CyclicGraphError(repr(d))
            initialNode = possibleInitialNodes.pop()
            
            for k, v in d.items():
                v.discard(initialNode)
            del d[initialNode]
            
            return [initialNode] + topologicalOrderingDestructive(d)
        
        return topologicalOrderingDestructive(copy.deepcopy(self._graph))


def rfilter(r, it, propFilter={}, invert=False):
    '''
    
    >>> list(rfilter(r'^.o+$', ['foo', 'bar']))
    ['foo']
    
    >>> list(rfilter(r'^.o+$', ['foo', 'bar'], invert=True))
    ['bar']
    
    >>> list(rfilter(r'-(?P<x>[^-]+)-', ['fooo-baar-ooo', 'fooo-fooo-ooo'], propFilter={'x': r'o{3}'}))
    ['fooo-fooo-ooo']
    
    >>> list(rfilter(r'-(?P<x>[^-]+)-', ['fooo-.*-ooo', 'fooo-fooo-ooo', 'fooo-.+-ooo'], propFilter={'x': ['.*', '.+']}))
    ['fooo-.*-ooo', 'fooo-.+-ooo']
    
    '''
    
    # Supports Python 2 and 3
    if isinstance(r, str):
        r = re.compile(r)
    try:
        if isinstance(r, unicode):
            r = re.compile
    except NameError:
        pass
    
    for x in it:
        m = r.search(x)
        ok = False
        if m:
            ok = True
            if propFilter:
                d = m.groupdict()
                for k, v in propFilter.items():
                    if k in d:
                        if isinstance(v, basestring):
                            if not re.search(v, d[k]):
                                ok = False
                                break
                        else:
                            if d[k] not in v:
                                ok = False
                                break
        
        if invert:
            if not ok:
                yield x
        else:
            if ok:
                yield x


class SubprocessError(Exception):
    
    def __init__(self, out, err, returncode):
        self.out = out
        self.err = err
        self.returncode = returncode
        self.msg = repr('--- out ---\n%s\n--- err ---\n%s\n--- code: %d ---' % (self.out, self.err, self.returncode))


def communicateWithReturncode(cmd, input=None, **Popen_kwargs):
    if input is not None:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, **Popen_kwargs)
        (out, err) = p.communicate(input=input)
    else:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **Popen_kwargs)
        (out, err) = p.communicate()
    return out, err, p.returncode


def communicate(cmd, assertZero=False, input='', **Popen_kwargs):
    out, err, returncode = communicateWithReturncode(cmd, input=input, **Popen_kwargs)
    return (out, err)


def check_communicate(cmd, input='', **Popen_kwargs):
    out, err, returncode = communicateWithReturncode(cmd, input=input, **Popen_kwargs)
    if returncode != 0:
        raise SubprocessError(out, err, returncode)
    return (out, err)


