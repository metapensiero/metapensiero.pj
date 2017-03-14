## body_only: True
## enable_es6: True

def func():
    value = 0

    class MyError(Exception):
        pass

    class MySecondError(MyError):
        """A stupid error"""

    try:
        value += 1
        raise MyError("Something bad happened")
        value += 1
    except MySecondError:
        value += 20
    except MyError:
        value += 30
    except:
        value += 40
    finally:
        value += 1
