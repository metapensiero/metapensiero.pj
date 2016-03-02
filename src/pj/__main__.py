# -*- coding: utf-8 -*-
# :Project:  pj -- commandline interface
# :Created:    mar 01 mar 2016 19:33:21 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
#

import argparse

from . import api


parser = argparse.ArgumentParser(
    description="A Python 3 to ES6 JavaScript compiler",
    prog='pj'
)
parser.add_argument('files', metavar='file', type=str, nargs='+',
                    help="Python source file(s) to convert.")
parser.add_argument('-5', '--es5', dest='es5', action='store_true',
                    help="Also transpile to ES5 using BabelJS.")


def main():
    args = parser.parse_args()
    for fname in args.files:
        if args.es5:
            api.transpile_py_file(fname)
        else:
            api.translate_file(fname)

if __name__ == '__main__':
    main()
