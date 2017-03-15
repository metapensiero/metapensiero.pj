## requires: python_version >= (3,5)
## body_only: True
## enable_es6: True
## enable_stage3: True

def func():

    class A:

        async def method(self):
            pass

    class B(A):

        async def method(self):
            await super().method()
