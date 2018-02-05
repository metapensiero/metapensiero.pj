# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj -- public api
# :Created:  ven 26 feb 2016 15:16:13 CET
# :Author:   Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast
import base64
import json
import inspect
import logging
import os
import textwrap

import dukpy

from .processor.transforming import Transformer
from .processor.util import Block
from .js_ast import JSStatements
from . import transformations

log = logging.getLogger(__name__)

BABEL_COMPILER = os.path.join(os.path.dirname(__file__), 'data',
                              'babel-6.18.1.min.js')
BABEL_POLYFILL = os.path.join(os.path.dirname(__file__), 'data',
                              'polyfill.min.js')


def _calc_file_names(src_filename, dst_filename=None, map_filename=None):
    """Calculate destination paths for file translation/transpile."""
    src_filename = os.path.abspath(src_filename)
    src_dir = os.path.dirname(src_filename)
    if dst_filename and not os.path.isdir(dst_filename):
        dst_filename = os.path.abspath(dst_filename)
        dst_dir = os.path.dirname(dst_filename)
    else:
        if dst_filename and os.path.isdir(dst_filename):
            dst_dir = os.path.abspath(dst_filename)
        else:
            dst_dir = src_dir
        dst_name = os.path.basename(os.path.splitext(src_filename)[0])
        dst_filename = os.path.join(dst_dir, dst_name + '.js')
    if map_filename:
        map_filename = os.path.abspath(map_filename)
    else:
        map_filename = dst_filename + '.map'
    map_dir = os.path.dirname(map_filename)
    src_relpath = os.path.relpath(src_filename, map_dir)
    map_relpath = os.path.relpath(map_filename, dst_dir)
    return dst_filename, map_filename, src_relpath, map_relpath


def _inline_src_map(src_map):
    src_map_data = ('data:text/json;base64,%s' %
        base64.b64encode(src_map.encode('utf-8')).decode('ascii'))
    return '\n//# sourceMappingURL=%s\n' % src_map_data


def translate_file(src_filename, dst_filename=None, map_filename=None,
                   enable_es6=False, enable_stage3=False, inline_map=False):
    """Translate the given python source file to ES6 Javascript."""
    dst_filename, map_filename, src_relpath, map_relpath = _calc_file_names(
        src_filename, dst_filename, map_filename
    )
    src_text = open(src_filename).readlines()
    js_text, src_map = translates(src_text, True, src_relpath,
                                  enable_es6=enable_es6,
                                  enable_stage3=enable_stage3)
    if inline_map:
        js_text += src_map.stringify(inline_comment=True)
    else:
        js_text += '\n//# sourceMappingURL=%s\n' % map_relpath

    with open(dst_filename, 'w') as dst:
        dst.write(js_text)
    if not inline_map:
        with open(map_filename, 'w') as map:
            map.write(src_map.stringify())


def translate_object(py_obj, body_only=False, enable_es6=False,
                     enable_stage3=False):
    """Translate the given Python 3 object (function, class, etc.) to ES6
    Javascript.

    If `body_only` is ``True``, the object itself is discarded and only its
    body gets translated as it was a module body.

    Return a ``(js_text, js_source_map)`` tuple.
    """
    cwd = os.getcwd()
    src_filename = os.path.abspath(inspect.getsourcefile(py_obj))
    prefix = os.path.commonpath((cwd, src_filename))
    if len(prefix) > 1:
        src_filename = src_filename[len(prefix) + 1:]
    src_lines, sline_offset = inspect.getsourcelines(py_obj)
    # line offsets should be 0-based
    sline_offset = sline_offset - 1
    with open(src_filename) as f:
        complete_src = f.read()
    return translates(src_lines, True, src_filename, (sline_offset, 0),
                      body_only=body_only, complete_src=complete_src,
                      enable_es6=enable_es6, enable_stage3=enable_stage3)


def translates(src_text, dedent=True, src_filename=None, src_offset=None,
               body_only=False, complete_src=None, enable_es6=False,
               enable_stage3=False):
    """Translate the given Python 3 source text to ES6 Javascript.

    If the string comes from a file, it's possible to specify the filename
    that will be inserted into the output source map. The `src_offset` is the
    ``(line_offset, col_offset)`` tuple of the fragment and it's used to
    relocate the map segments. `map_filename` is the intended file name for
    the output map file that will be added as pragma comment to the output JS.

    Setting `body_only` to a true value will change the evaluation behavior to
    translate only the body of the first statement.
    """
    if isinstance(src_text, (tuple, list)):
        src_lines = src_text
        src_text = ''.join(src_text)
    else:
        src_lines = src_text.splitlines()  # removes \n

    # take into account only the lines with content because only those
    # will be dedented
    src_line_num = 0
    for l in src_lines:
        if not len(l.strip()) == 0:
            src_line_num += 1

    sline_offset, scol_offset = src_offset or (0, 0)
    if dedent:
        # remove indentation so that fragments of files with stuff not
        # at root can be evaluated, or ast will complain
        dedented = textwrap.dedent(src_text)
        if len(dedented) < len(src_text):
            scol_offset += (len(src_text) - len(dedented)) // src_line_num
    else:
        dedented = src_text
    t = Transformer(transformations, JSStatements, es6=enable_es6,
                    stage3=enable_stage3)
    pyast = ast.parse(dedented)
    if body_only and hasattr(pyast, 'body') and len(pyast.body) == 1 \
       and hasattr(pyast.body[0], 'body'):
        # if body_only is true, discard the top level element and and
        # take the first child as top, this will allow to use the body
        # of a function or class as it was a module bosy
        pyast = pyast.body[0]
        # naive check, remove the last statement if it's a return
        if isinstance(pyast.body[-1], ast.Return):
            pyast.body.pop()
    jsast = t.transform_code(pyast)
    dline_offset = dcol_offset = 0
    if t.snippets:
        snipast = t.transform_snippets()
        snipast += jsast
        jsast = snipast
    js_code_block = Block(jsast)
    js_text = js_code_block.read()
    if not src_filename:
        src_filename = '<source>'

    src_map = js_code_block.sourcemap(complete_src or src_text, src_filename,
                                      (sline_offset, scol_offset),
                                      (dline_offset, dcol_offset))
    for t in src_map.tokens:
        log.debug("js: (%d, %d)\t\t py: (%d, %d)\t txt: '%s'",
                  t.dst_line, t.dst_col, t.src_line - sline_offset,
                  t.src_col - scol_offset, t.mapping['text'])
    return js_text, src_map


def transpile_es6s(es6_text, es6_filename=None, es6_sourcemap=None,
                   enable_stage3=False, **kw):
    """Transpile the given ES6 Javascript to ES5 Javascript using Dukpy
    and babeljs."""
    opts = dict(sourceMaps=True)
    if es6_filename:
        opts['filename'] = es6_filename
    if es6_sourcemap:
        if isinstance(es6_sourcemap, str):
            es6_sourcemap = es6_sourcemap.encode()
        opts['inputSourceMap'] = es6_sourcemap
    opts['presets'] = ["es2015"]
    if enable_stage3:
        opts['presets'].append('stage-3')
    truntime = kw.pop('truntime', False)
    if truntime:
        opts['plugins'] = ['transform-runtime']
    res = babel_compile(es6_text, **opts)
    return res['code'], res['map']


def transpile_object(py_obj, body_only=False, es6_filename=None,
                     enable_stage3=False, **kw):
    """Transpile the given Python 3 object to ES5 Javascript using
    Dukpy and babeljs."""
    es6_text, es6_sourcemap = translate_object(py_obj, body_only=body_only,
                                               enable_es6=True,
                                               enable_stage3=enable_stage3)
    return transpile_es6s(es6_text, es6_filename, es6_sourcemap.encode(),
                          enable_stage3=enable_stage3, **kw)


def transpile_pys(src_text, dedent=True, src_filename=None, src_offset=None,
                  body_only=False, es6_filename=None, enable_stage3=False,
                  **kw):
    """Transpile the given Python 3 source text to ES5 Javascript
    using Dukpy and babeljs.
    """
    es6_text, es6_sourcemap = translates(src_text, dedent, src_filename,
                                         src_offset, body_only, enable_es6=True,
                                         enable_stage3=enable_stage3)
    return transpile_es6s(es6_text, es6_filename, es6_sourcemap,
                          enable_stage3=enable_stage3, **kw)


def transpile_py_file(src_filename, dst_filename=None, map_filename=None,
                      enable_stage3=False, **kw):
    """Transpile the given Python 3 source file to ES5 Javascript
    using Dukpy and babeljs.
    """
    dst_filename, map_filename, src_relpath, map_relpath = _calc_file_names(
        src_filename, dst_filename, map_filename
    )
    dst_name, dst_ext = os.path.splitext(dst_filename)
    map_name, map_ext = os.path.splitext(map_filename)
    es6_dst_filename = dst_name + '.es6' + dst_ext
    es6_map_filename = map_name + '.es6' + map_ext
    dst_dir = os.path.dirname(dst_filename)
    es6_map_relpath = os.path.relpath(es6_map_filename, dst_dir)
    es6_relpath = os.path.relpath(es6_dst_filename, dst_dir)
    src_text = open(src_filename).readlines()
    es6_text, es6_src_map = translates(
        src_text, True, src_relpath, enable_es6=True,
        enable_stage3=enable_stage3)

    es5_text, es5_src_map = transpile_es6s(es6_text, es6_relpath,
                                           es6_src_map.encode(),
                                           enable_stage3=enable_stage3, **kw)
    es5_text += '\n//# sourceMappingURL=%s\n' % map_relpath
    es6_text += '\n//# sourceMappingURL=%s\n' % es6_map_relpath

    with open(es6_dst_filename, 'w') as dst:
        dst.write(es6_text)
    with open(es6_map_filename, 'w') as map:
        map.write(es6_src_map.stringify())

    with open(dst_filename, 'w') as dst:
        dst.write(es5_text)
    with open(map_filename, 'w') as map:
        map.write(json.dumps(es5_src_map))


def evaljs(js_text, load_es6_polyfill=False, **kwargs):
    """Evaluate JS code, like ``dukpy.evaljs()``, optionally loading the es6
    polyfill before the actual code.
    """
    if isinstance(js_text, (str, bytes, bytearray)):
        js_text = [js_text]
    else:
        list(js_text)
    if load_es6_polyfill:
        with open(BABEL_POLYFILL, 'r', encoding='utf-8') as babel_poly:
            js_text = (['global = this; this.console = {log: print};\n'] +
                       [babel_poly.read()] + js_text)
    return dukpy.evaljs(js_text, **kwargs)


def eval_object(py_obj, append=None, body_only=False, ret_code=False,
                **kwargs):
    js_text, _ = translate_object(py_obj, body_only)
    if append:
        js_text += append
    res = dukpy.evaljs(js_text, **kwargs)
    if ret_code:
        res = (res, js_text)
    return res


def evals(py_text, body_only=False, ret_code=False, **kwargs):
    js_text, _ = translates(py_text, body_only=body_only)
    res = dukpy.evaljs(js_text, **kwargs)
    if ret_code:
        res = (res, js_text)
    return res


def eval_object_es6(py_obj, append=None, body_only=False, ret_code=False,
                    enable_stage3=False, **kwargs):
    es5_text, _ = transpile_object(py_obj, body_only,
                                   enable_stage3=enable_stage3)
    if append:
        es5_text += '\n' + append
    res = evaljs(es5_text, load_es6_polyfill=True, **kwargs)
    if ret_code:
        res = (res, es5_text)
    return res


def evals_es6(py_text, body_only=False, ret_code=False, enable_stage3=False,
              **kwargs):
    es5_text, _ = transpile_pys(py_text, body_only=body_only,
                                enable_stage3=enable_stage3)
    res = evaljs(es5_text, load_es6_polyfill=True, **kwargs)
    if ret_code:
        res = (res, es5_text)
    return res


BABEL_JS_CTX = None


def babel_compile(source, reuse_js_ctx=True, **kwargs):
    """Compile the given `source` from ES6 to ES5 usin Babeljs."""
    global BABEL_JS_CTX
    presets = kwargs.get('presets')
    if not presets:
        kwargs['presets'] = ["es2015"]
    trans_code = ('var bres, res;'
                  'bres = Babel.transform(dukpy.es6code, dukpy.babel_options);',
                  'res = {map: bres.map, code: bres.code};')
    if reuse_js_ctx and BABEL_JS_CTX:
        result = BABEL_JS_CTX.evaljs(trans_code, es6code=source,
                                     babel_options=kwargs)
    else:
        with open(BABEL_COMPILER, 'r', encoding='utf-8') as babel_js:
            if reuse_js_ctx:
                BABEL_JS_CTX = dukpy.JSInterpreter()
                eval_fn = BABEL_JS_CTX.evaljs
            else:
                eval_fn = dukpy.evaljs
            result = eval_fn(
                (babel_js.read(),
                 'var bres, res;'
                 'bres = Babel.transform(dukpy.es6code, dukpy.babel_options);',
                 'res = {map: bres.map, code: bres.code};'),
                es6code=source,
                babel_options=kwargs
            )
    return result
