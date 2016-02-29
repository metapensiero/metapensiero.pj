# -*- coding: utf-8 -*-
# :Project:  pj -- py evaluation tests
# :Created:    dom 28 feb 2016 16:27:40 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
#

import pytest

from pj.api import eval_object, eval_object_es5

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

    assert sum() == eval_object_es5(sum, 'sum();')

def test_list_in():

    def list_in():
        return [
            1 in [10, 11],
            2 in [10, 11],
            11 in [10, 11]
        ]

    # ocio!
    assert [True, False, False] == eval_object(list_in, 'list_in();')

def test_if_else_elif():

    def test_if():

        if 3 < 3:
            x = 1
        elif 2 < 3:
            x = 2
        else:
            x = 3
        return x

    assert test_if() == eval_object_es5(test_if, 'test_if();')

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

    assert _while() == eval_object_es5(_while, '_while();')

@pytest.mark.xfail
def test_list_comprehension():

    def _list():
        return  [x + 1 for x in [1, 2, 3, 100]]

    assert _list() == eval_object_es5(_list, '_list();')

def test_dict_member_deletion():

    def deletion():
        d = {'foo': 1, 'bar': 2}
        del d['bar']
        return d

    assert deletion() == eval_object_es5(deletion, 'deletion();')

def test_func_simple_arg():

    def f(x):
        return x + 1000

    assert f(7) == eval_object_es5(f, 'f(7);')

def test_for_range_simple():

    def dofor():
        x = 0
        for i in range(5):
            x += i
        return x

    assert dofor() == eval_object_es5(dofor, 'dofor();')

def test_for_range_less_simpler():

    def dofor():
        x = 0
        for i in range(3, 5):
            x += i
        return x

    assert dofor() == eval_object_es5(dofor, 'dofor();')

def test_for_items_in_dict():

    def dofor():
        x = ''
        d = {'foo': 'FOO', 'bar': 'BAR'}
        for k in dict(d):
            x += k + d[k]
        return x

    result = eval_object_es5(dofor, 'dofor();')
    assert result == 'fooFOObarBAR' or result == 'barBARfooFOO'

def test_for_items_in_array():

    def dofor():
        x = 0
        for t in [1, 2, 3, 100]:
            x += t
        return x

    assert dofor() == eval_object_es5(dofor, 'dofor();')
