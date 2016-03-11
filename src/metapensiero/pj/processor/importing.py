# -*- coding: utf-8 -*-
# :Project:  pj -- imports processor
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import os
import re

from .util import DirectedGraph


def orderedModules(sourcePath, mainModule):
    """Return a list of module names in an order that doesn't violate the
    [dependency graph](http://en.wikipedia.org/wiki/Dependency_graph)
    """
    digraph = dependencyGraph(sourcePath, mainModule)
    return list(digraph.topologicalOrdering)


def dependencyGraph(sourcePath, firstModule):

    digraph = DirectedGraph()

    todo = set([firstModule])
    done = set()

    while len(todo) > 0:

        module = todo.pop()
        done.add(module)

        digraph.addNode(module)

        # Load the code
        path = sourcePath.pathForModule(module)
        with open(path, 'r') as f:
            py = f.read()

        # Handle each prereq
        for prereq in parseImports(py):
            digraph.addArc(module, prereq)
            if prereq not in done:
                todo.add(prereq)

    return digraph


# Python code &rarr; list of imported modules
def parseImports(py):
    imports = []
    for line in py.split('\n'):
        for m in re.finditer(r'^\s*from[ \t]+([^ \t]+)[ \t]+import', line):
            imports.append(m.group(1) or m.group(2))
    return imports


class SourcePath:

    def __init__(self, folders):
        self.folders = folders

    def pathForModule(self, module, exts=['py', 'pj', 'js']):

        # Find all matches
        paths = []
        for folder in self.folders:
            for ext in exts:
                path = '%s/%s.%s' % (
                                        folder.rstrip('/'),
                                        '/'.join(module.split('.')),
                                        ext)
                if os.path.isfile(path):
                    paths.append(path)

        # Do we have exactly one match?
        if len(paths) == 1:
            return paths[0]
        elif len(paths) == 0:
            raise Exception('Module not found: "%s". Path: %s' % (module, repr(self.folders)))
        elif len(paths) > 1:
            raise Exception('Multiple files found for module "%s": %s' % (module, repr(paths)))
