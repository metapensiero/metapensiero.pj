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

    expected = (
        'AsyncFunctionDef(args=arguments(args=[], \n'
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
        '                 returns=None)'
    )
    assert dump == expected


def test_ast_class_super(astjs):

    class A:

        def __init__(self, value):
            self.value = value
            d = {'a': 1, 'b': 2}
            super().__init__(x, y)

        def meth(self):
            super().another_meth(x, y)

    expected = (
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
        '}\n'
    )

    assert str(astjs(A, es6=True)) == expected

def test_ast_import(astdump):

    def func():
        import foo, bar
        import foo.bar as b
        from foo.bar import hello as h, bye as bb
        from ..foo.zoo import bar
        from . import foo
        from .foo import bar

    node, dump = astdump(func)

    expected = (
        'FunctionDef(args=arguments(args=[], \n'
        '                           defaults=[], \n'
        '                           kw_defaults=[], \n'
        '                           kwarg=None, \n'
        '                           kwonlyargs=[], \n'
        '                           vararg=None), \n'
        '            body=[Import(names=[alias(asname=None, \n'
        "                                      name='foo'), \n"
        '                                alias(asname=None, \n'
        "                                      name='bar')]), \n"
        "                  Import(names=[alias(asname='b', \n"
        "                                      name='foo.bar')]), \n"
        '                  ImportFrom(level=0, \n'
        "                             module='foo.bar', \n"
        "                             names=[alias(asname='h', \n"
        "                                          name='hello'), \n"
        "                                    alias(asname='bb', \n"
        "                                          name='bye')]), \n"
        '                  ImportFrom(level=2, \n'
        "                             module='foo.zoo', \n"
        '                             names=[alias(asname=None, \n'
        "                                          name='bar')]), \n"
        '                  ImportFrom(level=1, \n'
        '                             module=None, \n'
        '                             names=[alias(asname=None, \n'
        "                                          name='foo')]), \n"
        '                  ImportFrom(level=1, \n'
        "                             module='foo', \n"
        '                             names=[alias(asname=None, \n'
        "                                          name='bar')])], \n"
        '            decorator_list=[], \n'
        "            name='func', \n"
        '            returns=None)'
    )

    assert dump == expected

def test_ast_all(astdump):

    def func():

        __all__ = ['foo', 'bar']

        __all__ = ('foo', 'bar')

    node, dump = astdump(func)

    expected = (
        'FunctionDef(args=arguments(args=[], \n'
 '                           defaults=[], \n'
        '                           kw_defaults=[], \n'
        '                           kwarg=None, \n'
        '                           kwonlyargs=[], \n'
        '                           vararg=None), \n'
        '            body=[Assign(targets=[Name(ctx=Store(), \n'
        "                                       id='__all__')], \n"
        '                         value=List(ctx=Load(), \n'
        "                                    elts=[Str(s='foo'), \n"
        "                                          Str(s='bar')])), \n"
        '                  Assign(targets=[Name(ctx=Store(), \n'
        "                                       id='__all__')], \n"
        '                         value=Tuple(ctx=Load(), \n'
        "                                     elts=[Str(s='foo'), \n"
        "                                           Str(s='bar')]))], \n"
        '            decorator_list=[], \n'
        "            name='func', \n"
        '            returns=None)'
    )

    assert dump == expected
