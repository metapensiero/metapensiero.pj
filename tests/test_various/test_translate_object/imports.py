## body_only: True
## enable_es6: True

def func():
    import foo, bar
    import foo.bar as b
    from foo.bar import hello as h, bye as bb
    from ..foo.zoo import bar
    from . import foo
    from .foo import bar

    from __globals__ import test_name

    from foo__bar import zoo
    import foo__bar as fb
    from __foo.bar import zoo
    import __foo.bar as fb
    from foo import __default__ as bar
    from at_tilde_.foo.bar import zoo

    # this should not trigger variable definition
    test_name = 2

    # this instead should do it
    test_foo = True

    __all__ = ['test_name', 'test_foo']
