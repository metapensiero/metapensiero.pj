## requires: python_version >= (3,8)
## first_stmt_only: True

def func():

    def afunc(a, b, *args, foo=None, **kwargs):
        acall(a, b, *args, foo=None, **kwargs)

        def bfunc(a, b, *, foo=None, **kwargs):
            pass

        def cfunc(a=1, b=2, *,foo=None):
            pass
