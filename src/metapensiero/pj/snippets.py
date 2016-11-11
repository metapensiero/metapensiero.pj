# -*- coding: utf-8 -*-
# :Project:  pj -- code to aid transformation, it gets converted
# :Created:  mar 01 mar 2016 01:42:26 CET
# :Author:   Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#


def _in(left, right):
    from __globals__ import Array, typeof

    if isinstance(right, Array) or typeof(right) == 'string':
        return right.indexOf(left) > -1
    else:
        return left in right


def _in_es6(left, right):
    from __globals__ import Array, typeof, Map, Set, WeakMap, WeakSet

    if isinstance(right, Array) or typeof(right) == 'string':
        return right.indexOf(left) > -1
    elif isinstance(right, (Map, Set, WeakMap, WeakSet)):
        return right.has(left)
    else:
        return left in right

def set_decorators(cls, props):

    for p in dict(props):
        decos = props[p]
        def reducer(val, deco):
            return deco(val, cls, p)
        deco = decos.reduce(reducer, cls.prototype[p])
        cls.prototype[p] = deco
