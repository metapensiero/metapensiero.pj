class Foo:

    @property
    def bar(self):

        return self

    @bar.setter
    def bar(self, value):
        self._bar = value

    zoo = 1
