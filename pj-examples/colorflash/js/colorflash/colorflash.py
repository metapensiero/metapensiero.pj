from mylib.color import Color
from mylib.tweening import Tween, easeInOut
from mylib.random import randint
from mylib.misc import bind


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
            document.body.style.background = (self._oldColor
                                                    ._interpolatedToward(self._newColor, t)
                                                    ._webString())

        def onComplete(t):
            document.title = self._newColor._webString()

        Tween({
            '_duration': TRANSITION_DURATION,
            '_callback': bind(callback, self),
            '_easing': easeInOut,
            '_onComplete': bind(onComplete, self),
        })

        setTimeout(
            bind(arguments.callee, self),
            CHANGE_EVERY)


def main():
    Controller()


window.colorflash = {
    'main': main,
}
