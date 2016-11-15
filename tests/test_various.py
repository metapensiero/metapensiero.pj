# -*- coding: utf-8 -*-
# :Project:  pyxc-pj -- tests for various stuff
# :Created:    lun 22 feb 2016 23:31:45 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
#

from metapensiero.pj.api import translate_object


def test_body_names_stop_at_func(astobj):

    from metapensiero.pj.processor.util import body_local_names

    def outer(no):
        yes = 1

        def yes_func():
            no2 = 3

        yes2 = 3

    assert body_local_names(astobj(outer).body) == {'yes', 'yes2'}


def test_textwrap_behavior():

    txt = " " * 4 + "foo bar" + "\n" + " " * 4 + "bar foo" + "\n"
    assert len(txt) == 24
    l = txt.splitlines()[0]
    assert len(l) == 11
    import textwrap
    out = textwrap.dedent(txt)
    assert len(out) == 16


def test_globals():

    def func():

        def simple_alert():
            window.alert('Hi there!')

        el = document.querySelector('button')
        el.addEventListener('click', simple_alert)


    expected = ('var el;\n'
                'function simple_alert() {\n'
                '    window.alert("Hi there!");\n'
                '}\n'
                'el = document.querySelector("button");\n'
                'el.addEventListener("click", simple_alert);\n')

    assert translate_object(func, body_only=True)[0] == expected


def test_imports():

    def func():
        import foo, bar
        import foo.bar as b
        from foo.bar import hello as h, bye as bb
        from ..foo.zoo import bar
        from . import foo
        from .foo import bar

        from __globals__ import test_name

        from foo__bar import zoo
        import foo__bar as fb
        # this should not trigger variable definition
        test_name = 2

        # this instead should do it
        test_foo = True

        __all__ = ['test_name', 'test_foo']

    expected = ('var test_foo;\n'
                "import * as foo from 'foo';\n"
                "import * as bar from 'bar';\n"
                "import * as b from 'foo/bar';\n"
                "import {hello as h, bye as bb} from 'foo/bar';\n"
                "import {bar} from '../foo/zoo';\n"
                "import * as foo from './foo';\n"
                "import {bar} from './foo';\n"
                "import {zoo} from 'foo-bar';\n"
                "import * as fb from 'foo-bar';\n"
                'test_name = 2;\n'
                'test_foo = true;\n'
                'export {test_name};\n'
                'export {test_foo};\n')

    assert translate_object(func, body_only=True, enable_es6=True)[0] == expected


def test_exception():

    def func():

        class MyError(Exception):
            pass

        class MySecondError(MyError):
            """A stupid error"""

    expected = (
        'function MyError(message) {\n'
        '    this.name = "MyError";\n'
        '    this.message = (message || "Custom error MyError");\n'
        '    if (((typeof Error.captureStackTrace) === "function")) {\n'
        '        Error.captureStackTrace(this, this.constructor);\n'
        '    } else {\n'
        '        this.stack = new Error(message).stack;\n'
        '    }\n'
        '}\n'
        'MyError.prototype = Object.create(Error.prototype);\n'
        'MyError.prototype.constructor = MyError;\n'
        'class MySecondError extends MyError {\n'
        '    /* A stupid error */\n'
        '}\n'
    )

    assert translate_object(func, body_only=True, enable_es6=True)[0] == expected


def test_try_except_simple():

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

    expected = (
        'var value;\n'
        'function MyError(message) {\n'
        '    this.name = "MyError";\n'
        '    this.message = (message || "Custom error MyError");\n'
        '    if (((typeof Error.captureStackTrace) === "function")) {\n'
        '        Error.captureStackTrace(this, this.constructor);\n'
        '    } else {\n'
        '        this.stack = new Error(message).stack;\n'
        '    }\n'
        '}\n'
        'MyError.prototype = Object.create(Error.prototype);\n'
        'MyError.prototype.constructor = MyError;\n'
        'class MySecondError extends MyError {\n'
        '    /* A stupid error */\n'
        '}\n'
        'try {\n'
        '    value = 0;\n'
        '    throw new MySecondError("This is an error");\n'
        '} catch(e) {\n'
        '    if ((e instanceof MySecondError)) {\n'
        '        value = 1;\n'
        '    } else {\n'
        '        throw e;\n'
        '    }\n'
        '}\n'
    )

    assert translate_object(func, body_only=True, enable_es6=True)[0] == expected


def test_try_except_complex():


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


    expected = (
        'var value;\n'
        'value = 0;\n'
        'function MyError(message) {\n'
        '    this.name = "MyError";\n'
        '    this.message = (message || "Custom error MyError");\n'
        '    if (((typeof Error.captureStackTrace) === "function")) {\n'
        '        Error.captureStackTrace(this, this.constructor);\n'
        '    } else {\n'
        '        this.stack = new Error(message).stack;\n'
        '    }\n'
        '}\n'
        'MyError.prototype = Object.create(Error.prototype);\n'
        'MyError.prototype.constructor = MyError;\n'
        'class MySecondError extends MyError {\n'
        '    /* A stupid error */\n'
        '}\n'
        'try {\n'
        '    value += 1;\n'
        '    throw new MyError("Something bad happened");\n'
        '    value += 1;\n'
        '} catch(e) {\n'
        '    if ((e instanceof MySecondError)) {\n'
        '        value += 20;\n'
        '    } else {\n'
        '        if ((e instanceof MyError)) {\n'
        '            value += 30;\n'
        '        } else {\n'
        '            value += 40;\n'
        '        }\n'
        '    }\n'
        '} finally {\n'
        '    value += 1;\n'
        '}\n'
    )

    assert translate_object(func, body_only=True, enable_es6=True)[0] == expected


def test_inner_method_func():

    def func():

        class Example:
            def foo(self):

                def bar():
                    pass


    expected = (
        'class Example {\n'
        '    foo() {\n'
        '        var bar;\n'
        '        bar = () => {\n'
        '        };\n'
        '    }\n'
        '}\n'
    )

    assert translate_object(func, body_only=True, enable_es6=True)[0] == expected
    # test that multiple levels of nested functions all gets translated to
    # arrow functions
    def func2():

        class Example:
            def foo(self):

                def bar():

                    def zoo():
                        pass


    expected = (
        'class Example {\n'
        '    foo() {\n'
        '        var bar;\n'
        '        bar = () => {\n'
        '            var zoo;\n'
        '            zoo = () => {\n'
        '            };\n'
        '        };\n'
        '    }\n'
        '}\n'
    )

    assert translate_object(func2, body_only=True, enable_es6=True)[0] == expected


def test_str():

    def func():

        str(x)

    expected = 'x.toString();\n'

    assert translate_object(func, body_only=True, enable_es6=True)[0] == expected


def test_kwargs():

    def func():

        def with_kwargs(a, **kwargs):
            pass

        with_kwargs(1, foo=2, bar=3)

    expected = ('function with_kwargs(a, kwargs = {}) {\n}\n'
                'with_kwargs(1, {foo: 2, bar: 3});\n')

    assert translate_object(func, body_only=True, enable_es6=True)[0] == expected


def test_properties():

    class Foo:

        @property
        def bar(self):
            return self._bar

        @bar.setter
        def bar(self, value):
            self._bar = value

    expected = (
        'class Foo {\n'
        '    get bar() {\n'
        '        return this._bar;\n'
        '    }\n'
        '    set bar(value) {\n'
        '        this._bar = value;\n'
        '    }\n'
        '}\n'
    )

    assert translate_object(Foo, enable_es6=True)[0] == expected


def test_special_methods():

    # it seems that if name this class the same of the previous test,
    # inspect.getsourcelines will found that instead of this...
    class Foo2:

        def __len__(self):
            return 5

        def __str__(self):
            return 'bar'

    expected = (
        'class Foo2 {\n'
        '    get length() {\n'
        '        return 5;\n'
        '    }\n'
        '    toString() {\n'
        '        return "bar";\n'
        '    }\n'
        '}\n'
    )

    assert translate_object(Foo2, enable_es6=True)[0] == expected


def test_special_methods2():

    class Foo3:

        @classmethod
        def foo(self):
            return 'bar'

    expected = (
        'class Foo3 {\n'
        '    static foo() {\n'
        '        return "bar";\n'
        '    }\n'
        '}\n'
    )

    assert translate_object(Foo3, enable_es6=True)[0] == expected


def test_slices():

    def func():

        foo = 'foofoo'
        foo[1:]
        foo[:-1]
        foo[3:-1]
        foo[2]

    expected = (
        'function func() {\n'
        '    var foo;\n'
        '    foo = "foofoo";\n'
        '    foo.slice(1);\n'
        '    foo.slice(0, (- 1));\n'
        '    foo.slice(3, (- 1));\n'
        '    foo[2];\n'
        '}\n'
    )

    assert translate_object(func)[0] == expected


def test_init_local_def_with_return():
    """An __init__ with a function that returns something should not raise any
    concern."""

    class Foo4:
        def __init__(self):
            def bar():
                return 10
            self.bar = bar

    expected = (
        'class Foo4 {\n'
        '    constructor() {\n'
        '        var bar;\n'
        '        bar = () => {\n'
        '            return 10;\n'
        '        };\n'
        '        this.bar = bar;\n'
        '    }\n'
        '}\n'
    )
    assert translate_object(Foo4, enable_es6=True)[0] == expected


def test_isinstance():
    """test for ``isinstance(foo, (Bar, Zoo))`` to return a concatenated or
    instanceof expression.
    """

    def test_isi():
        a = isinstance(foo, (Bar, Zoo))

    expected = (
        'function test_isi() {\n'
        '    var a;\n'
        '    a = ((foo instanceof Bar) || (foo instanceof Zoo));\n'
        '}\n'
    )

    assert translate_object(test_isi, enable_es6=False)[0] == expected


def test_new_func():

    def test_new():
        a = new(foo())

    expected = (
        'function test_new() {\n'
        '    var a;\n'
        '    a = new foo();\n'
        '}\n'
    )

    assert translate_object(test_new, enable_es6=False)[0] == expected


def test_self_removed_on_function():

    def test_self_removed():
        def func(self, a, b):
            pass

    expected = (
        'function test_self_removed() {\n'
        '    function func(a, b) {\n'
        '    }\n'
        '}\n'
    )

    assert translate_object(test_self_removed, enable_es6=False)[0] == expected
