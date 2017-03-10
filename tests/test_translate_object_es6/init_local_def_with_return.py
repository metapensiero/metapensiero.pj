# An __init__ with a function that returns something should not raise any
# concern.

class Foo4:
    def __init__(self):
        def bar():
            return 10
        self.bar = bar
