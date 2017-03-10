def func():
    import foo, bar
    import foo.bar as b
    from foo.bar import hello as h, bye as bb
    from ..foo.zoo import bar
    from . import foo
    from .foo import bar
