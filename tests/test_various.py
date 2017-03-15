# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj -- tests for various stuff
# :Created:  lun 22 feb 2016 23:31:45 CET
# :Authors:  Alberto Berti <alberto@metapensiero.it>,
#            Lele Gaifax <lele@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

from metapensiero.pj.api import translate_object


def test_body_names_stop_at_func(astobj):

    from metapensiero.pj.processor.util import body_local_names

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


class TestTranslationFromFS:

    EXT = '.js'

    def test_translate_object(self, name, py_code, options, expected):
        dump = translate_object(py_code, **options)[0]
        assert dump.rstrip() == expected.rstrip()
