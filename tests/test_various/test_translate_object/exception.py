## body_only: True
## enable_es6: True

def func():

    class MyError(Exception):
        pass

    class MySecondError(MyError):
        """A stupid error"""
