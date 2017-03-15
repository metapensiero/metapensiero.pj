## body_only: True
## enable_es6: True

def func():

    def with_kwargs(a, **kwargs):
        pass

    with_kwargs(1, foo=2, bar=3)
