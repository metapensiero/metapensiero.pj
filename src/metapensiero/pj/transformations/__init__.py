# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj
# :Created:  gio 09 mar 2017 19:43:11 CET
# :Author:   Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast
from functools import wraps
import logging


from ..js_ast import JSKeySubscript, JSStr, TargetNode  # noqa: E402


logger = logging.getLogger(__name__)

if 'compiled' not in __package__:
    import macropy.activate  # noqa
    logger.info('Enabled macros expansion.')
else:
    logger.info('Using compiled transforms.')


def _normalize_name(n):
    if n.startswith('d_'):
        n = n.replace('d_', '$')
    elif n.startswith('dd_'):
        n = n.replace('dd_', '$$')
    # allow to reference names that are Python's keywords by appending
    # a dash to them
    elif not n.startswith('_') and n.endswith('_'):
        n = n[:-1]
    return n


def _normalize_dict_keys(transformer, keys):
    res = []
    for key in keys:
        if isinstance(key, str):
            key = ast.Str(key)
        elif isinstance(key, JSStr):
            key = ast.Str(key.args[0])
        if not isinstance(key, ast.Str):
            if transformer.enable_es6:
                key = JSKeySubscript(key)
            else:
                if isinstance(key, ast.AST):
                    py_node = key
                elif isinstance(key, TargetNode) and key.py_node is not None:
                    py_node = key.py_node
                else:
                    raise ValueError('Value of type %r cannot '
                                     'be use as key' % type(key))
                transformer.unsupported(py_node, True,
                                        'Value of type %r cannot '
                                        'be use as key' % type(key))
        res.append(key)
    return res


class Matcher:

    def __init__(self, match_func):
        self.match_func = match_func
        self.wrapper = None

    def wrap(self, func):
        from macropy.experimental.pattern import PatternMatchException
        matcher = self

        @wraps(func)
        def wrapper(t, x, **kw):
            try:
                vars = {k: v for k, v in matcher.match_func(x)}
                return func(t, x, **vars)
            except PatternMatchException:
                pass
        self.wrapper = wrapper
        return self

    def __call__(self, *args, **kw):
        if self.wrapper is None:
            return self.wrap(*args, **kw)
        return self.wrapper(*args, **kw)


match = Matcher
