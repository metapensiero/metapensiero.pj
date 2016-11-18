# -*- coding: utf-8 -*-
# :Project:  pj -- py evaluation tests
# :Created:    dom 28 feb 2016 16:27:40 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
#

import pytest

from metapensiero.pj.api import eval_object, eval_object_es6, translate_object


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


def test_for_range_step():

    def dofor():
        x = 0
        for i in range(0, 10, 2):
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

    assert test_class() == eval_object_es6(test_class, 'test_class();')


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

    assert test_class() == eval_object_es6(test_class, 'test_class();')


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

    assert test_class() == eval_object_es6(test_class, 'test_class();')


def test_class_assigns():

    def test_class_js():

        class Animal:

            is_big = False

            def __init__(self, name):
                self.name = name

        res = []
        teddy = Animal('teddy')
        list(res).append(teddy.is_big)
        grizzly = Animal('Bigbear')
        grizzly.is_big = True
        list(res).append(grizzly.is_big)
        list(res).append(teddy.is_big)

        return res

    def test_class():

        class Animal:

            is_big = False

            def __init__(self, name):
                self.name = name

        res = []
        teddy = Animal('teddy')
        res.append(teddy.is_big)
        grizzly = Animal('Bigbear')
        grizzly.is_big = True
        res.append(grizzly.is_big)
        res.append(teddy.is_big)

        return res

    assert test_class()  == eval_object_es6(test_class_js, 'test_class_js();')

def test_method_decorators():

    def test_deco():

        def currency(func, cls, name):
            def wrapper(tax):
                return '€ ' + str(func.bind(self)(tax))
            return wrapper

        class Product:

            def __init__(self, price):
                self.price = price

            @currency
            def euro_price_with_tax(self, tax_rate_perc):
                return self.price * (1 + (tax_rate_perc * 0.01))

        foo = Product(80)
        return foo.euro_price_with_tax(22)

    def test_deco_py():

        def currency(func):
            def wrapper(self, tax):
                return '€ ' + str(func(self, tax))
            return wrapper

        class Product:

            def __init__(self, price):
                self.price = price

            @currency
            def euro_price_with_tax(self, tax_rate_perc):
                return self.price * (1 + (tax_rate_perc * 0.01))

        foo = Product(80)
        return foo.euro_price_with_tax(22)


    assert test_deco_py()  == eval_object_es6(test_deco, 'test_deco();')


def test_class_decorators():

    def test_class_deco():

        counter = 0
        res = []

        def deco(cls):
            def wrapper(self, *args):
                counter += 1
                res.push(counter)
                return cls.prototype.constructor.call(self, *args)
            wrapper.prototype = cls.prototype
            return wrapper

        @deco
        class DecoTest:

            def __init__(self, res):
                self.res = res

            def foo(self):
                return self.res

        a = DecoTest()
        b = DecoTest()
        c = DecoTest('bar')

        return res, isinstance(c, DecoTest), c.foo() == 'bar'

    assert [[1, 2, 3], True, True]  == eval_object_es6(test_class_deco, 'test_class_deco();')


def test_type():

    def test_type_js():

        class Foo:
            pass

        a = Foo()
        b = Foo()

        res = type(a) is type(b) and type(b) is Foo.prototype
        return res

    def test_type_py():

        class Foo:
            pass

        a = Foo()
        b = Foo()

        res = type(a) is type(b) and type(b) is Foo
        return res

    assert test_type_py()  == eval_object_es6(test_type_js, 'test_type_js();')


def test_for_of():

    def test_forof_js():

        from __globals__ import iterable, Set

        a = [1,2,3,4,5]

        b = Set(['a', 'b'])

        a_v = []
        b_k = []

        for v in iterable(a):
            a_v.push(v)

        # Objects are not iterable so this should be empty
        for k in iterable(b):
            b_k.push(k)

        return a_v, b_k

    assert [[1,2,3,4,5], ['a', 'b']] == eval_object_es6(test_forof_js, 'test_forof_js();')

def test_for_inherited():

    def test_for_inh():

        def Foo():
            pass

        Foo.prototype = {
            'bar': 1
        }

        def Zoo():
            pass

        f = Foo()
        f.bar2 = 2

        Zoo.prototype = f

        z = Zoo()

        z_local = []
        z_all = []
        z_proto_local = []
        z_proto_all = []


        for k in dict(z, True):
            z_all.push(k);

        for k in dict(type(z)):
            z_proto_local.push(k);

        for k in dict(type(z), True):
            z_proto_all.push(k);

        return z_local, z_all, z_proto_local, z_proto_all

    assert [[], ['bar2', 'bar'], ['bar2'], ['bar2', 'bar']] == eval_object_es6(test_for_inh, 'test_for_inh();')

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
    assert test_try() == eval_object_es6(test_try, 'test_try();')


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
    assert test_try() == eval_object_es6(test_try, 'test_try();')

def test_call_rest():

    def test_rest():

        a = [1, 2, 3, 4, 5]

        def rest(*values):
            res = 0
            for i in values:
                res += i

            return res

        return rest(*a)

    assert test_rest() == 15

    assert test_rest() == eval_object_es6(test_rest, 'test_rest();')


def test_call_kw():

    def test_kw():

        def kw(a=1,*, b=3, c=5):
            return a + b + c

        return kw()

    assert test_kw() == 9
    assert test_kw() == eval_object_es6(test_kw, 'test_kw();')

    def test_kw2(a, c):

        def kw(a=1,*, b=3, c=5):
            return a + b + c

        return kw(a, c=c)

    assert test_kw2(1, 1) == 5
    assert test_kw2(1, 1) == eval_object_es6(test_kw2, 'test_kw2(1, 1);')

    def test_kw3(foo, bar):

        def kw(foo, **kwargs):
            return foo + kwargs['bar']

        return kw(foo, bar=bar)

    assert test_kw3(5, 10) == 15
    assert test_kw3(5, 10) == eval_object_es6(test_kw3, 'test_kw3(5, 10);')


def test_slices():

    def test():

        foo = 'fooFoo'
        a = [
            foo[1],
            foo[-3:],
            foo[2:-1],
            foo[:5]
        ]
        return a

    assert test() == ['o', 'Foo', 'oFo', 'fooFo'] == eval_object(test, 'test();')


def test_dict_update():

    def test_js_du():

        a = {
            'first': 1,
            'second': 'b'
        }

        b = {
            'second': 'c',
            'third': [],
        }

        dict(a).update(b)

        return a['second'], a['third']

    def test():

        a = {
            'first': 1,
            'second': 'b'
        }

        b = {
            'second': 'c',
            'third': [],
        }

        a.update(b)

        return a['second'], a['third']

    assert list(test()) == eval_object_es6(test_js_du, 'test_js_du();')


def test_dict_copy():

    def test_js_dc():

        a = {
            'first': 1,
            'second': 'b'
        }

        b  = dict(a).copy()

        return b['first'], b['second']

    def test():

        a = {
            'first': 1,
            'second': 'b'
        }

        b = a.copy()

        return b['first'], b['second']

    assert list(test()) == eval_object_es6(test_js_dc, 'test_js_dc();')


def test_in_map():

    def js_in_map():
        from __globals__ import Map

        m = Map();
        o = {};
        oo = {};
        m.set(o, 'test')
        return o in m, oo in o, m.get(o)

    assert [True, False, 'test'] == eval_object_es6(js_in_map, 'js_in_map();')


def test_yield():

    def test_y(r):

        def gen():
            for i in range(r):
                yield i

        return [*gen()]

    assert test_y(5) == eval_object_es6(test_y, 'test_y(5);')


def test_yield_from():

    def test_yf(r):

        def gen():
            yield from gen2()

        def gen2():
            for i in range(r):
                yield i

        return [*gen()]

    assert test_yf(5) == eval_object_es6(test_yf, 'test_yf(5);')


def test_yield_method():

    def test_ym(r):

        class Demo:

            def gen(self, r):
                for i in range(r):
                    yield i

        d = Demo()

        return [*d.gen(r)]

    assert test_ym(5) == eval_object_es6(test_ym, 'test_ym(5);')


def test_yield_in_method():

    def test_yim(r):

        class Demo:

            def __init__(self, r):
                self.r = r

            def foo(self):

                def gen():
                    for i in range(self.r):
                        yield i
                return [*gen()]

        d = Demo(r)

        return d.foo()

    assert test_yim(5) == eval_object_es6(test_yim, 'test_yim(5);')


def test_assert():

    def test_ass():

        try:
            assert False, "Error raised"
        except Exception as e:
            return e
        return True

    assert {'message': 'Error raised', 'name': 'PJAssertionError'} == eval_object(test_ass, 'test_ass();')


def test_classmethod():

    def test_cm():

        class CMTest:

            prop = 1

            @classmethod
            def creator(self):
                return new(self())

        return CMTest.creator().prop

    assert eval_object_es6(test_cm, 'test_cm();') == 1


def test_in_weakset():

    def test_in_ws():

        w = WeakSet()
        def prova():
            pass

        w.add(prova)
        return prova in w

    assert eval_object_es6(test_in_ws, 'test_in_ws();') == True
