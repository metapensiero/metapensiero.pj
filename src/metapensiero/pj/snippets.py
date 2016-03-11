# -*- coding: utf-8 -*-
# :Project:  pj -- code to aid transformation, it gets converted
# :Created:    mar 01 mar 2016 01:42:26 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
#

def _in(left, right):
    if isinstance(right, Array) or typeof(right) == 'string':
        return right.indexOf(left) > -1
    else:
        return left in right
