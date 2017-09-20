# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj
# :Created:  gio 09 mar 2017 19:43:11 CET
# :Author:   Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast
import logging

import macropy.activate

from ..js_ast import JSKeySubscript, JSStr, TargetNode

logger = logging.getLogger(__name__)


def _normalize_name(n):
    if n.startswith('d_'):
        n = n.replace('d_', '$')
    elif n.startswith('dd_'):
        n = n.replace('dd_', '$$')
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
                logger.warning('Ambiguous dict key %r and es6 disabled', key)
        res.append(key)
    return res
