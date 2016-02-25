# -*- coding: utf-8 -*-
# :Project:  pyxc-pj -- pyxc tests
# :Created:    lun 22 feb 2016 23:31:45 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
#



def test_body_names_stop_at_func(astobj):

    from pyxc.util import body_local_names

    def outer(no):
        yes = 1

        def yes_func():
            no2 = 3

        yes2 = 3

    assert body_local_names(astobj(outer).body) == {'yes', 'yes_func', 'yes2'}

def test_convert_block(astjs):

    def func(value):

        if value is True:
            value = 4
            for i in range(len(value)):
                v = value[i+1]
                other_func()
                v = other_func2()
            return value
        else:
            return 'no'

    import inspect
    import textwrap
    from pyxc.util import Block
    b = Block(astjs(func))
    src = textwrap.dedent(inspect.getsource(func))
    smap = b.sourcemap(src, 'test.py')
    assert smap == ''
