# -*- coding: utf-8 -*-
# :Project:   metapensiero.pj -- utils
# :Created:   gio 08 feb 2018 01:27:59 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Alberto Berti
#

JS_KEYWORDS = set([
    'break', 'case', 'catch', 'continue', 'default', 'delete', 'do', 'else',
    'finally', 'for', 'function', 'if', 'in', 'instanceof', 'new', 'return',
    'switch', 'this', 'throw', 'try', 'typeof', 'var', 'void', 'while', 'with',
    'abstract', 'boolean', 'byte', 'char', 'class', 'const',
    'double', 'enum', 'export', 'extends', 'final', 'float', 'goto',
    'implements', 'import', 'int', 'interface', 'long', 'native', 'package',
    'private', 'protected', 'public', 'short', 'static', 'super',
    'synchronized', 'throws', 'transient', 'volatile'])

# see https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Lexical_grammar
JS_KEYWORDS_ES6 = {
    'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
    'default', 'delete', 'do', 'else', 'export', 'extends', 'finally', 'for',
    'function', 'if', 'import', 'in', 'instanceof', 'new', 'return', 'super',
    'switch', 'this', 'throw', 'try', 'typeof', 'var', 'void', 'while', 'with',
    'yield'}

# Future keywords
JS_KEYWORDS_ES6.union({
    'enum', 'implements', 'interface', 'let', 'package', 'private',
    'protected', 'public', 'static', 'await'})

# Additional
JS_KEYWORDS_ES6.union({'null', 'true', 'false'})


def _check_keywords(target_node, name):
    trans = target_node.transformer
    if trans is not None:
        trans.unsupported(
            target_node.py_node,
            (name in JS_KEYWORDS_ES6 if trans.enable_es6 else name
             in JS_KEYWORDS),
            "Name '%s' is reserved in JavaScript." % name)
    else:
        if name in JS_KEYWORDS:
            raise ValueError("Name %s is reserved in JavaScript." % name)
