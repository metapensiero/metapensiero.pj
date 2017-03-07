def func():

    class A:

        async def method(self):
            pass

    class B(A):

        async def method(self):
            await super().method()
