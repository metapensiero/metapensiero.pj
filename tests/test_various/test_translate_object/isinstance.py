## enable_es6: True

# test for ``isinstance(foo, (Bar, Zoo))`` to return a concatenated or
# instanceof expression.

def test_isi():
    a = isinstance(foo, (Bar, Zoo))
