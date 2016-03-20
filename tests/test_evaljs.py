# -*- coding: utf-8 -*-
# :Project:  pj -- py evaluation tests
# :Created:    dom 28 feb 2016 16:27:40 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
#

import pytest

from metapensiero.pj.api import eval_object, eval_object_es5, translate_object

def test_bitwise_xor():

    def xor():
        return [0 ^ 0, 0 ^ 1, 1 ^ 0, 1 ^ 1]

    assert xor() == eval_object(xor, 'xor();')

def test_bitwise_and():

    def _and():
        return [0 & 0, 0 & 1, 1 & 0, 1 & 1]

    assert _and() == eval_object(_and, '_and();')

def test_bitwise_or():

    def _or():
        return [0 | 0, 0 | 1, 1 | 0, 1 | 1]

    assert _or() == eval_object(_or, '_or();')

def test_bitwise_not():

    def _not():
        return [~(-2), ~(-1), ~(0), ~(1), ~(2)]

    assert _not() == eval_object(_not, '_not();')

def test_rshift():

    def rshift():
        return [64 >> 2, 65 >> 2, -16 >> 3]

    assert rshift() == eval_object(rshift, 'rshift();')

def test_multiple_assignement_and_sum():

    def sum():
        x = y = 2
        return x + y

    assert sum() == eval_object(sum, 'sum();')

def test_list_in():

    def list_in():
        return [
            1 in [10, 11],
            'foo' in 'barfoobar',
            11 in [10, 11]
        ]

    assert list_in() == eval_object(list_in, 'list_in();')
    expected = (
        'var _pj;\n'
        'function _pj_snippets(container) {\n'
        '    function _in(left, right) {\n'
        '        if (((right instanceof Array) || ((typeof right) === "string"))) {\n'
        '            return (right.indexOf(left) > (- 1));\n'
        '        } else {\n'
        '            return (left in right);\n'
        '        }\n'
        '    }\n'
        '    container["_in"] = _in;\n'
        '    return container;\n'
        '}\n'
        '_pj = {};\n'
        '_pj_snippets(_pj);\n'
        'function list_in() {\n'
        '    return [_pj._in(1, [10, 11]), _pj._in("foo", "barfoobar"), _pj._in(11, '
        '[10, 11])];\n'
        '}\n'
    )
    assert translate_object(list_in)[0] == expected

def test_if_else_elif():

    def test_if():

        if 3 < 3:
            x = 1
        elif 2 < 3:
            x = 2
        else:
            x = 3
        return x

    assert test_if() == eval_object(test_if, 'test_if();')

def test_while_and_aug_assignement():

    def _while():
        x = 0
        i = 10
        while True:
            x += i
            i -= 1
            if i < 0:
                break
            else:
                continue

        return x

    assert _while() == eval_object(_while, '_while();')

@pytest.mark.xfail
def test_list_comprehension():

    def _list():
        return  [x + 1 for x in [1, 2, 3, 100]]

    assert _list() == eval_object(_list, '_list();')

def test_dict_member_deletion():

    def deletion():
        d = {'foo': 1, 'bar': 2}
        del d['bar']
        return d

    assert deletion() == eval_object(deletion, 'deletion();')

def test_func_simple_arg():

    def f(x):
        return x + 1000

    assert f(7) == eval_object(f, 'f(7);')

def test_for_range_simple():

    def dofor():
        x = 0
        for i in range(5):
            x += i
        return x

    assert dofor() == eval_object(dofor, 'dofor();')

def test_for_range_less_simpler():

    def dofor():
        x = 0
        for i in range(3, 5):
            x += i
        return x

    assert dofor() == eval_object(dofor, 'dofor();')

def test_for_items_in_dict():

    def dofor():
        x = ''
        d = {'foo': 'FOO', 'bar': 'BAR'}
        for k in dict(d):
            x += k + d[k]
        return x

    result = eval_object(dofor, 'dofor();')
    assert result == 'fooFOObarBAR' or result == 'barBARfooFOO'

def test_for_items_in_array():

    def dofor():
        x = 0
        for t in [1, 2, 3, 100]:
            x += t
        return x

    assert dofor() == eval_object(dofor, 'dofor();')

def test_class_simple():

    def test_class():
        class Foo:
            def __init__(self):
                self.msg = 'foo'
        return Foo().msg

    assert test_class() == eval_object_es5(test_class, 'test_class();')

def test_class_inherit():

    def test_class():

        class Animal:
            def __init__(self, name):
                self.name = name

        class TalkingAnimal(Animal):
            def __init__(self, name, catchphrase):
                super().__init__(name)
                self.catchphrase = catchphrase
            def caption(self):
                return self.name + " sez '" + self.catchphrase + "'"

        return TalkingAnimal('Pac-Man', 'waka waka').caption()

    assert test_class() == eval_object_es5(test_class, 'test_class();')

def test_class_super():

    def test_class():

        class Animal:
            def __init__(self, name):
                self.name = name
        class TalkingAnimal(Animal):
            def __init__(self, name, catchphrase):
                super().__init__(name)
                self.catchphrase = catchphrase
            def caption(self):
                return self.name + " sez '" + self.catchphrase + "'"
        class Kitteh(TalkingAnimal):
            def __init__(self, name):
                super().__init__(name, 'OH HAI')
            def caption(self):
                return 'OMG AWESOMECUTE: ' + super().caption()

        return Kitteh('Maru-san').caption()

    assert test_class() == eval_object_es5(test_class, 'test_class();')


def test_try_except_simple():

    def test_try():
        value = 0
        try:
            value += 1
            raise 'a string error'
            value += 1
        except:
            value += 1
        finally:
            value += 1
        return value

    assert test_try() == 3
    assert test_try() == eval_object_es5(test_try, 'test_try();')


def test_try_except_complex():

    def test_try():
        value = 0

        class MyError(Exception):
            pass

        class MySecondError(MyError):
            """A stupid error"""

        try:
            value += 1
            raise MyError("Something bad happened")
            value += 1
        except MySecondError:
            value += 20
        except MyError:
            value += 30
        except:
            value += 40
        finally:
            value += 1
        return value

    assert test_try() == 32
    assert test_try() == eval_object_es5(test_try, 'test_try();')
