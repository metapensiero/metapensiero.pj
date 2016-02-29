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

    expected = ''.join('AsyncFunctionDef(args=arguments(args=[], \n'
                       '                                defaults=[], \n'
                       '                                kw_defaults=[], \n'
                       '                                kwarg=None, \n'
                       '                                kwonlyargs=[], \n'
                       '                                vararg=None), \n'
                       "                 body=[Import(names=[alias(asname='aio', \n"
                       "                                           name='asyncio')]), \n"
                       '                       Assign(targets=[Name(ctx=Store(), \n'
                       "                                            id='a')], \n"
                       "                              value=BinOp(left=Str(s='abc'), \n"
                       '                                          op=Mult(), \n'
                       '                                          right=Num(n=3))), \n'
                       '                       Assign(targets=[Name(ctx=Store(), \n'
                       "                                            id='b')], \n"
                       '                              value=BinOp(left=Num(n=2), \n'
                       '                                          op=Pow(), \n'
                       '                                          right=Num(n=3)))], \n'
                       '                 decorator_list=[], \n'
                       "                 name='func', \n"
                       '                 returns=None)')
    assert dump == expected


def test_ast_class_super(astjs):

    class A:

        def __init__(self, value):
            self.value = value
            d = {'a': 1, 'b': 2}
            super().__init__(x, y)

        def meth(self):
            super().another_meth(x, y)

    expected = ''.join((
        'class A {\n'
        '    constructor(value) {\n'
        '        var d;\n'
        '        this.value = value;\n'
        '        d = {"a": 1, "b": 2};\n'
        '        super(x, y);\n'
        '    }\n'
        '    meth() {\n'
        '        super.another_meth(x, y);\n'
        '    }\n'
        '}\n')
    )

    assert str(astjs(A)) == expected
