# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj
# :Author:   Andrew Schaaf <andrew@andrewschaaf.com>
# :License:  See LICENSE file
#

from .math import clamp


def linear(t):
    return t

def easeIn(t):
    return 1 - Math.pow(1 - t, 3)

def easeOut(t):
    return t * t * t

def easeInOut(t):
    return 3 * t * t - 2 * t * t * t


#<pre>Tween({
#   '_duration': 1000,
#   '_callback': lambda t: console.log(t),
#   '_easing': easeIn, # Default: linear
#})</pre>
class Tween:

    def __init__(self, info):

        self._startedAt = Date().getTime()

        self._duration = info._duration
        self._callback = info._callback
        self._easing = info._easing or linear

        self._tick()

    def _tick(self):

        t = clamp((Date().getTime() - self._startedAt) / self._duration, 0, 1)

        self._callback(t)

        if t < 1:
            setTimeout(self._tick.bind(self), 1)


__all__ = ('Tween', 'easeInOut')
