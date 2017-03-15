# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj -- tests
# :Created:  lun 22 feb 2016 12:50:26 CET
# :Authors:  Alberto Berti <alberto@metapensiero.it>,
#            Lele Gaifax <lele@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

class TestASTFromFS:

    EXT = {'test_ast_dump': '.ast', 'test_ast_es6': '.js'}

    def test_ast_dump(self, name, py_code, options, expected, astdump):
        node, dump = astdump(py_code, **options)
        dump = '\n'.join(line.rstrip() for line in dump.splitlines()).rstrip()
        assert dump == expected.rstrip()

    def test_ast_es6(self, name, py_code, options, expected, astjs):
        dump = str(astjs(py_code, **options))
        dump = '\n'.join(line.rstrip() for line in dump.splitlines()).rstrip()
        assert dump == expected.rstrip()
