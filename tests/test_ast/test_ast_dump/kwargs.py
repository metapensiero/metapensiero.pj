## requires: python_version < (3,8)
def func():

    def test(a, **kwargs):
        pass

    test(1, pippo=2, **kwargs)
