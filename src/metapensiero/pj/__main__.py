# -*- coding: utf-8 -*-
# :Project:  pj -- commandline interface
# :Created:    mar 01 mar 2016 19:33:21 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
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
parser.add_argument('files', metavar='file', type=str, nargs='+',
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
                    help="Add trasform runtime as plugin during transpile")
parser.add_argument('-o', '--output', type=str,
                    help="Output file/directory where to save the generated "
                    "code")
parser.add_argument('-d', '--debug', action='store_true',
                    help="Enable error reporting")
parser.add_argument('--pdb', action='store_true',
                    help="Enter post-mortem debug when an error occurs")


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
    if transpile:
        api.transpile_py_file(src_fname, dst_fname,
                              enable_stage3=enable_stage3,
                              **kw)
    else:
        api.translate_file(src_fname, dst_fname, enable_es6=enable_es6,
                           enable_stage3=enable_stage3)


def check_interpreter_supported():
    if sys.version_info < (3, 5):
        raise UnsupportedPythonError('JavaScripthon needs at least'
                                     ' Python 3.5 to run')


def main(args=None, fout=None, ferr=None):
    result = 0
    rep = Reporter(fout, ferr)
    args = parser.parse_args(args)
    freeargs = {
        'truntime': args.truntime
    }
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    if args.output and len(args.files) > 1:
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
                    rep.print_err("An error occured during processing.")
                rep.print_err(error)
            result = 1
    sys.exit(result)


if __name__ == '__main__':
    main()
