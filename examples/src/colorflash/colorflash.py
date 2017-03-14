# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj
# :Author:   Andrew Schaaf <andrew@andrewschaaf.com>
# :License:  See LICENSE file
#

from mylib.color import Color
from mylib.tweening import Tween, easeInOut
from mylib.random import randint


CHANGE_EVERY = 1000
TRANSITION_DURATION = 250


class Controller:

    def __init__(self):
        self._newColor = self._oldColor = Color(255, 255, 255)
        self._changeColor()

    def _changeColor(self):

        self._oldColor = self._newColor
        self._newColor = Color(
                randint(0, 255),
                randint(0, 255),
                randint(0, 255))

        def callback(t):
            transient_color = self._oldColor._interpolatedToward(self._newColor, t)
            document.body.style.background = transient_color ._webString()

        def onComplete(t):
            document.title = self._newColor._webString()

        Tween({
            '_duration': TRANSITION_DURATION,
            '_callback': callback,
            '_easing': easeInOut,
            '_onComplete': onComplete,
        })

        setTimeout(self._changeColor.bind(self), CHANGE_EVERY)


def main():
    Controller()


window.colorflash = {
    'main': main,
}
