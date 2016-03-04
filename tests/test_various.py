# -*- coding: utf-8 -*-
# :Project:  pyxc-pj -- tests for various stuff
# :Created:    lun 22 feb 2016 23:31:45 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
#

from pj.api import translate_object


def test_body_names_stop_at_func(astobj):

    from pj.processor.util import body_local_names

    def outer(no):
        yes = 1

        def yes_func():
            no2 = 3

        yes2 = 3

    assert body_local_names(astobj(outer).body) == {'yes', 'yes2'}

def test_textwrap_behavior():

    txt = " " * 4 + "foo bar" + "\n" + " " * 4 + "bar foo" + "\n"
    assert len(txt) == 24
    l = txt.splitlines()[0]
    assert len(l) == 11
    import textwrap
    out = textwrap.dedent(txt)
    assert len(out) == 16


def test_globals():

    def func():

        def simple_alert():
            window.alert('Hi there!')

        el = document.querySelector('button')
        el.addEventListener('click', simple_alert)


    expected = ('var el;\n'
                'function simple_alert() {\n'
                '    window.alert("Hi there!");\n'
                '}\n'
                'el = document.querySelector("button");\n'
                'el.addEventListener("click", simple_alert);\n')

    assert translate_object(func, body_only=True)[0] == expected


def test_imports():

    def func():
        import foo, bar
        import foo.bar as b
        from foo.bar import hello as h, bye as bb
        from ..foo.zoo import bar
        from . import foo
        from .foo import bar

        from __globals__ import test_name

        # this should not trigger variable definition
        test_name = 2

        # this instead should do it
        test_foo = True

        __all__ = ['test_name', 'test_foo']

    expected = ('var test_foo;\n'
                "import * as foo from 'foo';\n"
                "import * as bar from 'bar';\n"
                "import * as b from 'foo/bar';\n"
                "import {hello as h, bye as bb} from 'foo/bar';\n"
                "import {bar} from '../../foo/zoo';\n"
                "import * as foo from './foo';\n"
                "import {bar} from './foo';\n"
                'test_name = 2;\n'
                'test_foo = true;\n'
                'export test_name;\n'
                'export test_foo;\n')

    assert translate_object(func, body_only=True, enable_es6=True)[0] == expected
