# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj
# :Author:   Andrew Schaaf <andrew@andrewschaaf.com>
# :License:  See LICENSE file
#

# 'Random number from [0.0, 1.0)'
def random():
    x = Math.random()
    return 0 if x == 1 else x


# Assumes a, b are integers and
# returns a random integer from [a, b]
def randint(a, b):
    return Math.floor(random() * (b - a + 1)) + a

__all__ = ('random', 'randint')
