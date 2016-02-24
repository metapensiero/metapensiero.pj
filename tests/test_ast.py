# -*- coding: utf-8 -*-
# :Project:  pyxc-pj -- tests
# :Created:    lun 22 feb 2016 12:50:26 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
#



def test_ast_func(astdump):

    async def func():
        import asyncio as aio
        a = 'abc' * 3
        b = 2**3

    node, dump = astdump(func)

    assert dump == ""
