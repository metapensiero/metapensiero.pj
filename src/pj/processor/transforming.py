# -*- coding: utf-8 -*-
# :Project:  pj -- transformation processor
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast
import inspect
import os
import sys
import textwrap

from .exceptions import NoTransformationForNode
from .util import (rfilter, parent_of, random_token,
                   Line, Part, obj_source, body_local_names)

SNIPPETS_TEMPLATE ="""\
def _pj_snippets(container):
%(snippets)s
%(assignements)s
    return container

_pj = {}
_pj_snippets(_pj)

"""

ASSIGN_TEMPLATE="    container['%(name)s'] = %(name)s"


class TargetNode:

    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return ''.join(
            str(x) for x in
            self.serialize())

    def serialize(self):
        for a in self.emit(*self.transformed_args):
            yield from a.serialize()

    def lines(self, items, *, indent=False, delim=False):
        if not isinstance(items, (tuple, list)):
            items = (items,)
        for i in self._chain(items):
            yield self.line(i, indent=indent, delim=delim)

    def line(self, item, indent=False, delim=False):
        if isinstance(item, Line):
            item.indent += int(indent)
            l = item
        elif isinstance(item, (tuple, list)):
            item = tuple(self._chain(item))
            l = Line(self, item, indent, delim)
        else:
            l = Line(self, item, indent, delim)
        return l

    def part(self, *items):
        return Part(self, *self._expand(items))

    def _expand(self, items):
        return [i.serialize() if isinstance(i, TargetNode) else i for i in items]

    def _chain(self, items):
        for i in self._expand(items):
            if inspect.isgenerator(i):
                yield from i
            else:
                yield i


class Transformer:

    def __init__(self, py_ast_module, statements_class, snippets=True):
        self.transformations = load_transformations(py_ast_module)
        self.statements_class = statements_class
        self.snippets = set()
        self.enable_snippets = snippets

    def transform_code(self, py):

        top = ast.parse(py)
        body = top.body

        self.node_parent_map = build_node_parent_map(top)

        result = self.statements_class(body)
        self._finalize_target_node(result)

        self.node_parent_map = None

        return result

    def parent_of(self, node):
        return self.node_parent_map.get(node)

    def find_parent(self, node, cls):
        """Retrieve the first parent of the given ast node that is an instance
        of the given class."""
        parent = self.parent_of(node)
        if parent is not None:
            if isinstance(parent, cls):
                return parent
            else:
                return self.find_parent(parent, cls)

    def new_name(self):
        #LATER: generate better names
        return random_token(20)

    def add_snippet(self, code):
        self.snippets.add(code)

    def _transform_node(self, py_node):
        """This transforms a Python ast node to JS."""

        if isinstance(py_node, list) or isinstance(py_node, tuple):
            return [self._transform_node(child) for child in py_node]

        elif isinstance(py_node, ast.AST):
            # transformations can come in tuples or lists, take the
            # first one
            for transformation in self.transformations.get(
                    py_node.__class__.__name__, []):
                transformed = transformation(self, py_node)
                if transformed is not None:
                    self._finalize_target_node(transformed, py_node=py_node)
                    return transformed
            raise NoTransformationForNode(repr(py_node))

        elif isinstance(py_node, TargetNode):
            self._finalize_target_node(py_node)
            return py_node

        else:
            # e.g. an integer
            return py_node

    def _finalize_target_node(self, tnode, py_node=None):
        tnode.py_node = py_node
        tnode.transformed_args = [self._transform_node(arg) for arg in tnode.args]
        tnode.transformer = self

    def transform_snippets(self):
        snippets = tuple(self.snippets)
        srcs = [obj_source(s) for s in snippets]
        src = textwrap.indent('\n'.join(srcs), ' ' * 4)
        names = [s.__name__ for s in snippets]
        assign_src = '\n'.join([ASSIGN_TEMPLATE % {'name': n} for n in names])
        trans_src = SNIPPETS_TEMPLATE % {
            'snippets': src,
            'assignements': assign_src
        }
        t = Transformer.__new__(Transformer)
        t.transformations = self.transformations
        t.statements_class = self.statements_class
        t.snippets = None
        t.enable_snippets = False
        return t.transform_code(trans_src)


#### Helpers

def python_ast_names():
    #LATER: do this properly
    return rfilter(r'[A-Z][a-zA-Z]+', dir(ast))


def load_transformations(py_ast_module):
    # transformationsDict = {
    #     'NodeName': [...transformation functions...]
    # }
    d = {}
    astNames = list(python_ast_names())
    filenames = rfilter(
        r'^[^.]+\.py$',
        os.listdir(parent_of(py_ast_module.__file__)))
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


def build_node_parent_map(top):

    node_parent_map = {}

    def _process_node(node):
        for k in node._fields:
            x = getattr(node, k)
            if not (isinstance(x, list) or isinstance(x, tuple)):
                x = [x]
            for y in x:
                if isinstance(y, ast.AST):
                    node_parent_map[y] = node
                    _process_node(y)

    _process_node(top)

    return node_parent_map
