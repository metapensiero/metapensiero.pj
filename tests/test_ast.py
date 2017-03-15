# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj -- tests
# :Created:  lun 22 feb 2016 12:50:26 CET
# :Authors:  Alberto Berti <alberto@metapensiero.it>,
#            Lele Gaifax <lele@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

def test_ast_dump(fstest, astdump):
    name, py_code, options, expected = fstest
    node, dump = astdump(py_code, **options)
    dump = '\n'.join(line.rstrip() for line in dump.splitlines()).rstrip()
    assert dump == expected.rstrip()


def test_ast_es6(fstest, astjs):
    name, py_code, options, expected = fstest
    dump = str(astjs(py_code, **options))
    dump = '\n'.join(line.rstrip() for line in dump.splitlines()).rstrip()
    assert dump == expected.rstrip()
