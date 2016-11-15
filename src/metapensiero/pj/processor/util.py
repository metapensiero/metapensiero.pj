# -*- coding: utf-8 -*-
# :Project:  pj -- transformation utilities
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast
import copy
import inspect
import itertools
import random
import re
import textwrap

from . import sourcemaps


IGNORED_NAMES = ('__all__',)


def delimited(delimiter, arr, dest=None, at_end=False):
    if dest is None:
        dest = []
    if arr:
        dest.append(arr[0])
    for i in range(1, len(arr)):
        dest.append(delimiter)
        dest.append(arr[i])
    if at_end:
        dest.append(delimiter)
    return dest


def parent_of(path):
    return '/'.join(path.rstrip('/').split('/')[:-1])


def body_top_names(body):
    names = set()
    for x in body:
        names |= node_names(x)
    return names


def controlled_ast_walk(node):
    """Walk ast just like ast.walk(), but expect True on every branch to
    descend on sub-branches."""
    if isinstance(node, list):
        l = node.copy()
    elif isinstance(node, tuple):
        l = list(node)
    else:
        l = [node]
    while len(l) > 0:
        popped = l.pop()
        check_children = (yield popped)
        if check_children:
            for n in ast.iter_child_nodes(popped):
                l.append(n)

CODE_BLOCK_STMTS = (ast.FunctionDef, ast.ClassDef,
                    ast.AsyncFunctionDef)


def walk_under_code_boundary(node):
    it = controlled_ast_walk(node)
    traverse = None
    try:
        while True:
            subn = it.send(traverse)
            yield subn
            if isinstance(subn, CODE_BLOCK_STMTS):
                traverse = False # continue traversing sub names
            else:
                traverse = True
    except StopIteration:
        pass


def body_local_names(body):
    """Find the names assigned to in the provided body. It doesn't descent
    into function or class subelements."""
    names = set()
    for stmt in body:
        for subn in walk_under_code_boundary(stmt):
            if not isinstance(subn, CODE_BLOCK_STMTS):
                names |= node_names(subn)
    return names


def node_names(x):
    names = set()
    if isinstance(x, ast.Assign):
        for target in x.targets:
            if isinstance(target, ast.Name) and target.id not in \
               IGNORED_NAMES:
                names.add(target.id)
    elif isinstance(x, (ast.FunctionDef, ast.ClassDef)):
        names.add(x.name)
    return names


def rfilter(r, it, invert=False):
    """
    >>> list(rfilter(r'^.o+$', ['foo', 'bar']))
    ['foo']

    >>> list(rfilter(r'^.o+$', ['foo', 'bar'], invert=True))
    ['bar']

    """
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
        if invert:
            if not ok:
                yield x
        else:
            if ok:
                yield x


class OutputSrc:

    def __init__(self, node, name=None):
        self.node = node
        self.src_name = name

    def _gen_mapping(self, text, src_line=None, src_offset=None, dst_offset=None):
        """Generate a single mapping. `dst_line` is absent from signature
        because the part hasn't this information, but is present in the
        returned mapping. `src_line` is adjusted to be 0-based.

        See `Source Map version 3 proposal
        <https://docs.google.com/document/d/1U1RGAehQwRypUTovF1KRlpiOFze0b-_2gc6fAH0KY0k>`_.
        """
        return {
            'src_line': src_line - 1 if src_line else None,
            'src_offset': src_offset,
            'dst_line': None,
            'dst_offset': dst_offset,
            'text': text,
            'name': self.src_name if self.src_name is not True else str(self),
            'part': self
        }

    def _pos_in_src(self):
        """Returns the position in source of the generated node"""
        py_node = self.node.py_node
        if py_node:
            offset = getattr(py_node, 'col_offset', 0)
            # multi-line comments have an offset of -1
            if offset < 0:
                offset = 0
            result = (getattr(py_node, 'lineno', None),
                      offset)
        else:
            result = (None, None)
        return result


class Line(OutputSrc):

    def __init__(self, node, item, indent=False, delim=False, name=None):
        super().__init__(node, name)
        self.indent = int(indent)
        self.delim = delim
        if isinstance(item, (tuple, list)):
            item = Part(node, *item)
        self.item = item

    def __str__(self):
        line = str(self.item)
        if self.delim:
            line += ';'
        if self.indent:
            line = (' ' * 4 * self.indent) + line
        line += '\n'
        return line

    def serialize(self):
        yield self

    def src_mappings(self):
        src_line, src_offset = self._pos_in_src()
        offset = self.indent * 4
        if isinstance(self.item, str):
            if src_line:
                yield self._gen_mapping(self.item, src_line, src_offset,
                                        offset)
        else:
            assert isinstance(self.item, Part)
            for m in self.item.src_mappings():
                m['dst_offset'] += offset
                yield m

    def __repr__(self):
        return '<%s indent: %d, "%s">' % (self.__class__.__name__,
                                          self.indent, str(self))


class Part(OutputSrc):

    def __init__(self, node, *items, name=None):
        super().__init__(node, name)
        self.items = []
        for i in items:
            if isinstance(i, (str, Part)):
                self.items.append(i)
            elif inspect.isgenerator(i):
                self.items.extend(i)
            else:
                self.items.append(str(i))

    def __str__(self):
        return ''.join(str(i) for i in self.items)

    def serialize(self):
        yield self

    def src_mappings(self):
        src = str(self)
        src_line, src_offset = self._pos_in_src()
        frag = ''
        col = 0
        for i in self.items:
            assert isinstance(i, (str, Part))
            if isinstance(i, str):
                frag += i
            elif isinstance(i, Part):
                if frag and src_line:
                    yield self._gen_mapping(frag, src_line, src_offset, col)
                    col += len(frag)
                    frag = ''
                psrc = str(i)
                yield from i._translate_src_mappings(i, src, psrc, col)
                col += len(psrc)
        else:
            if frag and src_line:
                yield self._gen_mapping(frag, src_line, src_offset, col)

    def _translate_src_mappings(self, part, src=None, psrc=None, start=None):
        src = src or str(self)
        psrc = psrc or str(part)
        offset = src.find(psrc, start)
        for m in part.src_mappings():
            m['dst_offset'] += offset
            yield m

    def __repr__(self):
        return '<%s, "%s">' % (self.__class__.__name__,
                               str(self))


class Block(OutputSrc):

    def __init__(self, node):
        super().__init__(None)
        self.lines = list(node.serialize())

    def src_mappings(self, src_offset=None):
        sline_offset, scol_offset = src_offset or (0, 0)
        for ix, line in enumerate(self.lines, start=0):
            for m in line.src_mappings():
                m['dst_line'] = ix
                m['src_line'] += sline_offset
                m['src_offset'] += scol_offset
                yield m

    def read(self):
        return ''.join(str(l) for l in self.lines)

    def sourcemap(self, source, src_filename, src_offset=None):
        Token = sourcemaps.Token
        tokens = []
        for m in self.src_mappings(src_offset):
            token = Token(m['dst_line'], m['dst_offset'], src_filename,
                          m['src_line'], m['src_offset'], m['name'])
            tokens.append(token)

        src_map = sourcemaps.SourceMap(
            sources_content={src_filename: source}
        )
        for t in tokens:
            src_map.add_token(t)
        return sourcemaps.encode(src_map)


def obj_source(obj):
    src = inspect.getsource(obj)
    src = textwrap.dedent(src)
    return src
