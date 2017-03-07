def func():

    class MyError(Exception):
        pass

    class MySecondError(MyError):
        """A stupid error"""

    try:
        value = 0
        raise MySecondError('This is an error')
    except MySecondError:
        value = 1
