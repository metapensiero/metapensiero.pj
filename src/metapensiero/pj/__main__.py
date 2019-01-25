# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj -- commandline interface
# :Created:  mar 01 mar 2016 19:33:21 CET
# :Author:   Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import argparse
from collections import deque
import logging
from pathlib import Path
import sys

from . import api

log = logging.getLogger(__name__)


class UnsupportedPythonError(Exception):
    """Exception raised if the running interpreter version is
    unsupported.
    """


parser = argparse.ArgumentParser(
    description="A Python 3.5+ to ES6 JavaScript compiler",
    prog='pj'
)
parser.add_argument('files', metavar='file', type=str, nargs='*',
                    help="Python source file(s) or directory(ies) "
                    "to convert. When it is a directory it will be "
                    "converted recursively")
parser.add_argument('--disable-es6', dest='es6', action='store_false',
                    default=True,
                    help="Disable ES6 features during conversion"
                    " (Ignored if --es5 is specified)")
parser.add_argument('--disable-stage3', dest='stage3', action='store_false',
                    default=True,
                    help="Disable ES7 stage3 features during conversion")
parser.add_argument('-5', '--es5', dest='es5', action='store_true',
                    help="Also transpile to ES5 using BabelJS.")
parser.add_argument('--transform-runtime', action='store_true', dest='truntime',
                    help="Add transform runtime as plugin during transpile")
parser.add_argument('-o', '--output', type=str,
                    help="Output file/directory where to save the generated "
                    "code")
parser.add_argument('-d', '--debug', action='store_true',
                    help="Enable error reporting")
parser.add_argument('--pdb', action='store_true',
                    help="Enter post-mortem debug when an error occurs")
parser.add_argument('-s', '--string', type=str,
                    help="Convert a string, useful for small snippets. If the string"
                    " is '-' will be read from the standard input.")
parser.add_argument('-e', '--eval', action='store_true',
                    help="Evaluate the string supplied with the -s  using the"
                    " embedded interpreter and return the last result. This will "
                    "convert the input string with all the extensions enabled "
                    "(comparable to adding the '-5' option) and so it will take"
                    " some time because of BabelJS load times.")
parser.add_argument('--dump-ast', action='store_true',
                    help="Dump the Python AST. You need to have the package"
                    " metapensiero.pj[test] installed")
parser.add_argument('--inline-map', action='store_true',
                    help="Save the source-map inline instead of in an additional"
                    " file, useful when transpiling with BabelJS externally "
                    "but without access to the cli. Ignored "
                    "when transpiling.")
parser.add_argument('--source-name', help="When using '-s' together with"
                    " '--inline-map' this option is necessary to produce a"
                    " valid sourcemap which needs a name for the source file")


class Reporter:
    def __init__(self, fout=None, ferr=None):
        self.fout = fout or sys.stdout
        self.ferr = ferr or sys.stderr

    def print_err(self, *args, **kwargs):
        kwargs['file'] = self.ferr
        print(*args, **kwargs)

    def print(self, *args, **kwargs):
        kwargs['file'] = self.fout
        print(*args, **kwargs)


def transform(src_fname, dst_fname=None, transpile=False, enable_es6=False,
              enable_stage3=False, **kw):
    kw.pop('source_name', None)
    if transpile:
        kw.pop('inline_map', None)
        api.transpile_py_file(src_fname, dst_fname,
                              enable_stage3=enable_stage3,
                              **kw)
    else:
        kw.pop('truntime', None)
        api.translate_file(src_fname, dst_fname, enable_es6=enable_es6,
                           enable_stage3=enable_stage3, **kw)


def transform_string(input, transpile=False, enable_es6=False,
                     enable_stage3=False, **kw):
    inline_map = kw.get('inline_map', False)
    source_name = kw.get('source_name', None)
    if inline_map and source_name is None:
        raise ValueError("A source name is needed, please specify it using "
                         "the '--source-name option.")
    if transpile:
        res, src_map = api.transpile_pys(input, enable_stage3=enable_stage3,
                                         src_filename=source_name)
    else:
        res, src_map = api.translates(input, enable_es6=enable_es6,
                                      enable_stage3=enable_stage3,
                                      src_filename=source_name)
    if kw.get('inline_map', False):
        res += src_map.stringify(inline_comment=True)
    return res


def check_interpreter_supported():
    if sys.version_info < (3, 5):
        raise UnsupportedPythonError('JavaScripthon needs at least'
                                     ' Python 3.5 to run')


def main(args=None, fout=None, ferr=None):
    result = 0
    rep = Reporter(fout, ferr)
    args = parser.parse_args(args)
    freeargs = {
        'truntime': args.truntime,
        'inline_map': args.inline_map,
        'source_name': args.source_name
    }
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
        log.debug('Log started')
    if not (args.files or args.string):
        rep.print_err("Error: You have to supply either a string with -s or a "
                      "filename")
        result = 3
    if args.eval and not args.string:
        rep.print_err("Error: You have to supply a string with -s when using "
                      "evaluation")
    elif args.string:
        check_interpreter_supported()
        input = args.string
        if input == '-':
            input = sys.stdin.read()
        if args.dump_ast:
            from .testing import ast_dumps
            rep.print(ast_dumps(input)[1])
        if args.eval:
            es6 = es5 = stage3 = True
        else:
            es5 = args.es5
            es6 = args.es6
            stage3 = args.stage3
        try:
            res = transform_string(input, es5, es6, stage3,
                                   **freeargs)
            if args.eval:
                res = api.evaljs(res, load_es6_polyfill=True)
            rep.print(res)
        except Exception as e:
            if args.pdb:
                import pdb
                pdb.post_mortem(e.__traceback__)
            elif args.debug:
                raise
            else:
                error = "%s: %s" % (e.__class__.__name__, e)
                rep.print_err("An error occurred while compiling source "
                              "from string")
                rep.print_err(error)
            result = 1
    elif args.output and len(args.files) > 1:
        rep.print_err("Error: only one source file is allowed when "
                      "--output is specified.")
        result = 2
    else:
        try:
            check_interpreter_supported()
            for fname in args.files:
                src = Path(fname)
                if not src.exists():
                    rep.print_err("Skipping non existent file '%s'" % src)
                    continue
                if args.output:
                    dst = Path(args.output)
                else:
                    dst = None
                if src.is_dir():
                    if dst and src != dst:
                        if dst.exists() and not dst.is_dir():
                            rep.print_err("Source is a directory but output exists "
                                          "and it isn't")
                            result = 1
                            break
                        if not dst.exists():
                            dst.mkdir()
                    src_root = src
                    dst_root = dst
                    src_dirs = deque([src_root])
                    while len(src_dirs) > 0:
                        sdir = src_dirs.popleft()
                        if dst_root:
                            ddir = dst_root / sdir.relative_to(src_root)
                            if not ddir.exists():
                                ddir.mkdir()
                        else:
                            ddir = None
                        for spath in sdir.iterdir():
                            if spath.name in ('__pycache__', '__init__.py'):
                                continue
                            elif spath.is_dir():
                                src_dirs.append(spath)
                                continue
                            elif spath.suffix == '.py':
                                try:
                                    transform(
                                        str(spath),
                                        str(ddir) if ddir else None,
                                        args.es5,
                                        args.es6,
                                        args.stage3,
                                        **freeargs
                                    )
                                    rep.print("Compiled file %s" % spath)
                                except Exception as e:
                                    e.src_fname = spath
                                    raise
                else:
                    try:
                        transform(fname, args.output, args.es5, args.es6,
                                  args.stage3, **freeargs)
                        rep.print("Compiled file %s" % fname)
                    except Exception as e:
                        e.src_fname = fname
                        raise
        except Exception as e:
            if args.pdb:
                import pdb
                pdb.post_mortem(e.__traceback__)
            elif args.debug:
                raise
            else:
                src_fname = getattr(e, 'src_fname', None)
                error = "%s: %s" % (e.__class__.__name__, e)
                if src_fname:
                    rep.print_err("An error occurred while compiling source "
                                  "file '%s'" % src_fname)
                else:
                    rep.print_err("An error occurred during processing.")
                rep.print_err(error)
            result = 1
    sys.exit(result)


if __name__ == '__main__':
    main()
