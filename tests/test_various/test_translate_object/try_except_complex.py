## body_only: True
## enable_es6: True

def func():
    value = 0

    class MyError(Exception):
        pass

    class MySecondError(MyError):
        """A stupid error"""

    class MyThirdError(Exception):
        pass

    class MyFourthError(Exception):
        pass

    try:
        value += 1
        raise MyError("Something bad happened")
        value += 1
    except MySecondError as err:
        value += 20
    except (MyThirdError, MyFourthError) as err2:
        value += 30
    except MyError:
        value += 40
    except:
        value += 50
    finally:
        value += 1
